function(doc) {
  var data = doc;
  var id = data._id;
  var find_bid_by_lot = function(bids, id) {
    results = [];
    bids.forEach(function(bid) {
      bid.lotValues.forEach(function(value) {
        if ((value.relatedLot === id) && ((["invalid"].indexOf(value.status || "active") === -1))) {
          results.push(bid);
        }
      })
    });
    return results;
  }

  var filter_bids = function(bids) {
    var res = [];
    bids.forEach(function(bid) {
      if ((["invalid", "deleted"].indexOf(bid.status || "active") === -1)&&(bid.date > "2016-04-01")) {
        res.push(bid);
      }
    });
    return res;

  }
  var emit_results = function(data) {

    var date = (data.qualificationPeriod || {}).startDate || (data.awardPeriod || {}).startDate || null;
    var bids_start_date = data.tenderPeriod.startDate || null;
    if ((date) && (data.procurementMethod === "open") && (data.mode !== "test")) {
        if (("bids" in data) && ("lots" in data)) {
            var audits =[];
            data.lots.forEach(function(lot) {
            lot.documents.forEach(function(d){
                if (d.title.match(re)) {
                    if (audits.length > 0) {
                        if (audits[0].dateModified > d.dateModified) {
                             audits.pop();
                             audits.push(d)
                        }
                    } else {
                    	audits.push(d);
                    }
                }
            });
          
          

          var lot_id = lot.id;
          var bids_filtered = filter_bids(data.bids);
          var bids = find_bid_by_lot(bids_filtered, lot_id);
          for (var bid_id in bids) {
            var bid = bids[bid_id]
            var owner = bid.owner;
            emit([owner, bid.date], {
                tender: id,
                lot: lot_id,
                value: lot.value.amount,
                currency: lot.value.currency,
                bid: bid.id,
                audits: audits[0],
            })

          }

        });
      } else if ("bids" in data) {
        var bids = filter_bids(data.bids);
        var re = /audit/;
        var audits = [];
        data.documents.forEach(function(d){
            if (d.title.match(re)) {
                audits.push(d);
            }
        });
        bids.forEach(function(bid) {
            var owner = bid.owner;
            emit([owner, bid.date], {
                tender: id,
                value: data.value.amount,
                currency: data.value.currency,
                bid: bid.id,
                audits: audits[0],
            })
        });

      };
    }
  }
  emit_results(data);
}
