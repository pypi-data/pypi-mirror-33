from pypif.obj.common.license import License
from pypif.obj.common.person import Person


def add_tags(pif, tags):
    """Add tags to a pif"""
    if tags:
        pif.tags = tags


def add_license(pif, license):
    """Add a license to a pif"""
    if license:
        pif.licenses = [License(name=license)]


def add_contact(pif, contact_name):
    """Add a contact to a pif"""
    if not contact_name:
        return

    contact = Person()
    toks = contact_name.split()
    email = next(x for x in toks if "@" in x)
    if email is not None:
        contact.email = email.lstrip("<").rstrip(">")
        toks.remove(email)
    contact.name = " ".join(toks)
    pif.contacts = [contact]