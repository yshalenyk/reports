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
    if ((date) && (data.procurementMethod === "open") && (data.mode !== "test")) {
      if (("bids" in data) && ("lots" in data)) {
        data.lots.forEach(function(lot) {
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
            emit([owner, bid.date], result);

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
          emit([owner, bid.date], result);
        });

      };
    }
  }
  emit_results(data);
}
