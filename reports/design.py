import couchdb.design



bids = '''function(doc) {
    var data = doc;
    var random = function () {
        var owners = ["it.ua", "netcast.com.ua", "privatmarket.ua", "prom.ua", "e-tender.biz", "public-bid.com.ua", "newtend.com"];

        return owners[Math.floor(Math.random() * owners.length)];
    }
    var id = data.id;


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
              var owner = random();
              bids.forEach(function (bid) {
                  if ("owner" in bid) {
                      owner = bid.owner;
                  }
              });
              for (var bid in bids) {
                  var result = {};
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
          var owner = random();
          bids.forEach(function (bid) {
              if ("owner" in bid) {
                  owner = bid.owner;
              }
          });
          bids.forEach(function(bid) {
              var result = {};
              result["tender"] = id;
              result["value"] = value;
              result["bid"] = bid.id;
              emit([owner, date], result);
          });

      };
    }

    emit_results(data);

}'''

bids_view = couchdb.design.ViewDefinition('report', 'bids', bids)
