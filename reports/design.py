import couchdb.design
import os 
basepath = os.path.dirname(__file__)


tenders = '''
function(doc) {
    var data = doc;
    var id = data._id;
    var date = data.contracts[0].documents[0].datePublished;

    var find_bid_by_lot = function(bids, id) {
       results = [];
       bids.forEach(function(bid) {
           bid.lotValues.forEach(function(value) {
               if (value.relatedLot === id) {
                   results.push(bid);
               }
           })
       });
       return results;
    }

    var filter_bids = function(bids) {
       var res = [];
       bids.forEach(function(bid) {
          if ("status" in bid) {
              if (bid.status !== "invalidBid" || bid.status !== "invalid" || bid.status !== "deleted") {
                   res.push(bid);
               }
           } else {
               res.push(bid);
           }
       });
       return res;

    }
    var emit_results = function(data) {



      if (("bids" in data) && ("lots" in data)) {
          data.lots.forEach(function (lot) {
              if (lot.status === 'complete') {
                var lot_id = lot.id;
                var bids_filtered = filter_bids(data.bids);
                var bids = find_bid_by_lot(bids_filtered, lot_id);

                bids.forEach(function (bid) {

                        var result = {};
                    var owner = bid.owner;
                    result["tender"] = id;
                    result["lot"] = lot_id;
                    result["value"] = lot.value.amount;
                    result["bid"] = bid.id;
                    emit([owner, date], result);
                });
             };
          });
      } else if ("bids" in data) {
          var value = data.value.amount;
          var bids = filter_bids(data.bids);
          if (data.status === "complete") {
                bids.forEach(function(bid) {
                   var result = {};
		   var owner = bid.owner;
                   result["tender"] = id;
                   result["value"] = value;
                   result["bid"] = bid.id;
                   emit([owner, date], result);
                });
          }
      };
    }

    emit_results(data);


}

'''

with open(os.path.join(basepath, 'bids.js')) as bids_file:
    bids = bids_file.read()


bids_owner_date = couchdb.design.ViewDefinition('report', 'bids_owner_date', bids)
tenders_owner_date = couchdb.design.ViewDefinition('report', 'tenders_owner_date', tenders)
#contracts_no_docs = couchdb.design.ViewDefinition('report', 'contracts_no_documents', contracts_without_documents)
