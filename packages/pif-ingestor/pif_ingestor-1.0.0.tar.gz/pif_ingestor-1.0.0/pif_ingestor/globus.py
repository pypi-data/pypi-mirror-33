import os
import json
import pypif

interval_time = 10
default_collection = 35  # MDF Test collection
#default_collection = 21  # MDF Open Collection

def push_to_globus(paths, metadata={}, collection=default_collection, source_endpoint=None, transfer_timeout=None, verbose=False):
    """Upload files in path to globus collection"""
    #TODO: Cleanup partial submission on error
    try:
        from globus_sdk import GlobusError, GlobusAPIError, TransferData
        from mdf_forge import toolbox
    except ImportError:
        raise ImportError("Install 'globus_sdk' and 'mdf_forge' before uploading to globus")

    metadata["Title"] = metadata.get("Title", "dummy title")
    metadata["Authors"] = metadata.get("Authors", [("Jane", "Doe")])
    metadata["Publication Date"] = metadata.get("Publication Date", {"Year": 1776})
    metadata["Publisher"] = metadata.get("Publisher", "Citrine")
    metadata["Description"] = metadata.get("Description", "Testing dataset")

    # Set up clients
    config = {
        "app_name": "PIF Ingestor",
        "services": ["transfer", "publish"]
        }
    clients = toolbox.login(config)
    transfer_client = clients["transfer"]
    publish_client = clients["publish"]
    if not source_endpoint:
        source_endpoint = toolbox.get_local_ep(transfer_client)

    # Process metadata
    if not metadata.get("accept_license"):
        usr_res = input("Do you accept the license for collection " + str(collection) + "? y/n: ").strip().lower()
        if usr_res == 'y' or usr_res == "yes":
            metadata["accept_license"] = True

    # Upload the metadata
    result = publish_client.push_metadata(collection, metadata)
    dest_endpoint = result['globus.shared_endpoint.name']
    dest_path = os.path.join(result['globus.shared_endpoint.path'], "data")
    submission_id = result['id']
    if verbose:
        print("Metadata uploaded")

    # Transfer the file(s)
    tdata = TransferData(transfer_client, source_endpoint, dest_endpoint, notify_on_succeeded=False, notify_on_inactive=False, notify_on_failed=False)
    all_dests = []
    for source_path in paths:

        #TODO: Optimize this loop
        # Add each dir from the source path to the dest path, creating if needed on the dest ep
        full_dest_path = dest_path
        for dirc in os.path.dirname(source_path).strip("/").split("/"):
            full_dest_path = os.path.join(full_dest_path, dirc)
            try:
                transfer_client.operation_mkdir(dest_endpoint, full_dest_path)
            except GlobusAPIError as e:
                # If path already created, continue
                if e.http_status == 502:
                    pass
                else:
                    raise
        full_dest_path = os.path.join(full_dest_path, os.path.basename(source_path))
        all_dests.append(full_dest_path)

        tdata.add_item(os.path.abspath(source_path), full_dest_path, recursive=False)
    transfer_res = transfer_client.submit_transfer(tdata)

    # Wait for transfer to complete
    if transfer_res["code"] != "Accepted":
        raise GlobusError("Failed to transfer files: Transfer " + transfer_res["code"])
    else:
        if verbose:
            print("Data transfer submitted")
        while not transfer_client.task_wait(transfer_res["task_id"], timeout=interval_time, polling_interval=interval_time):
            for event in transfer_client.task_event_list(transfer_res["task_id"]):
                if event["is_error"]:
                    transfer_client.cancel_task(transfer_res["task_id"])
                    raise GlobusError("Error: " + event["description"])
                if transfer_timeout and interval_time >= transfer_timeout:
                    transfer_client.cancel_task(transfer_res["task_id"])
                    raise GlobusError("Transfer timed out.")
                if verbose:
                    print("Transferring...")
        if verbose:
            print("Transfer complete")

    # Complete publication
    fin_res = publish_client.complete_submission(submission_id)
    if verbose:
        print("Submission complete")
        print("Result:", fin_res.data)

    globus_urls = [dest_endpoint + dest_path for dest_path in all_dests]
    webapp_urls = ["https://www.globus.org/app/transfer?origin_id={}&origin_path={}".format(dest_endpoint, dest_path) for dest_path in all_dests]
    http_urls = ["https://data.materialsdatafacility.org/{}".format(dest_path) for dest_path in all_dests]
    path_map = {
        "globus_info": fin_res.data
        }

    for pos, orig in enumerate(paths):
        path_map[orig] = {
            "globus_url": globus_urls[pos],
            "webapp_url": webapp_urls[pos],
            "http_url": http_urls[pos]
            }

    return path_map

