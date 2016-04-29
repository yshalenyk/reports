import couchdb.design
import os 
basepath = os.path.dirname(__file__)


with open(os.path.join(basepath, 'bids.js')) as bids_file:
    bids = bids_file.read()

with open(os.path.join(basepath, 'tenders.js')) as tenders_file:
    tenders = tenders_file.read()



bids_owner_date = couchdb.design.ViewDefinition('report', 'bids_owner_date', bids)
tenders_owner_date = couchdb.design.ViewDefinition('report', 'tenders_owner_date', tenders)
#contracts_no_docs = couchdb.design.ViewDefinition('report', 'contracts_no_documents', contracts_without_documents)
