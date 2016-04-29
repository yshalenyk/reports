import couchdb.design



tenders = '''
function(doc) {
    
    var startDate = new Date(doc.enquiryPeriod.startDate);
    
    if (startDate < (new Date("2016-04-01T00:00+0300"))){
        return;
    }
    
    if (!(doc.procurementMethod==="open") ){
        return;
    }

    if ('mode' in doc) {
        if (doc.mode === 'test') {
            return;
        }
    }

    var max_date = function(contract) {
        var dates = [];

        if ('date' in contract) {
            dates.push(new Date(contract.date));
        }

        if ('dateSigned' in contract) {
            dates.push(new Date(contract.dateSigned));
        }
        if ('documents' in contract) {
            contract.documents.forEach(function (docm) {
                dates.push(new Date(docm.datePublished));
            });
        }
        var maxDate=new Date(Math.max.apply(null,dates));
        return mxDate.toISOString();
    }


    
    var emit_result = function (data) {


        var entity =  data.procuringEntity;
        if ('kind' in entity) {
             var kind = entity.kind;
        } else {
             var kind = '_kind';
        }

        var dateModified = data.dateModified;

        var owner = data.owner;

        data.contracts.forEach(function (contract) {
            if (contract.state === 'signed') {
                return;
            }
            var date = max_date(data.contract);
            if ('lots' in data) {
                var award_id = contract.awardID;
                
                data.awards.forEach(function (award) {
                    if (award.id === award_id) {
                        var lot_id = award.lotID;
                    }
                });

                data.lots.forEach(function(lot) {
                    if (lot.id  === lot_id) {
                        var value = lot.value.amount;
                    }
                });

                var result = {
                    tender: data._id,
                    value: value,
                    kind: kind,
                    datemodified: data.datemodified,
                }
                emit([owner, date], result);
            } else {
                var result = {
                    tender: data._id,
                    value: data.value,
                    kind: kind,
                    datemodified: data.datemodified,
                }
                emit([owner, date], result);

            }
            
        });
     }

    emit_result(doc);
}

'''


bids = '''
function (doc) {
    var data = doc;
    var id = data._id;


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

      var date = data.tenderPeriod.endDate;
      if (("bids" in data) && ("lots" in data)) {
          data.lots.forEach(function (lot) {
              var lot_id = lot.id;
              var bids_filtered = filter_bids(data.bids);
              var bids = find_bid_by_lot(bids_filtered, lot_id);
              for (var bid in bids) {
                  var result = {};
                  var owner = bids[bid].owner;
                  result["tender"] = id;
                  result["lot"] = lot_id;
                  result["value"] = lot.value.amount;
                  result["bid"] = bids[bid].id;
                  emit([owner, date], result);

              }

          });
      } else if ("bids" in data) {
          var value = data.value.amount;
          var bids = filter_bids(data.bids);
          bids.forEach(function(bid) {
              var result = {};
              var owner = bid.owner;
              result["tender"] = id;
              result["value"] = value;
              result["bid"] = bid.id;
              emit([owner, date], result);
          });

      };
    }
    

    emit_results(data);

}
'''



bids_owner_date = couchdb.design.ViewDefinition('report', 'bids_owner_date', bids)
tenders_owner_date = couchdb.design.ViewDefinition('report', 'tenders_owner_date', tenders)
#contracts_no_docs = couchdb.design.ViewDefinition('report', 'contracts_no_documents', contracts_without_documents)
