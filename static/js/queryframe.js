function $getform(element) {
    return element = document.getElementById(element);
}

function $setspread(targetid, px) {
    var d = $getform(targetid);
    var h = d.offsetHeight;
    var maxh = 100;

    function dmove() {
        h += 50; //设置层展开的速度
        if (h >= maxh) {
            d.style.height = px;
            clearInterval(iIntervalId);
        } else {
            d.style.display = 'block';
            d.style.height = h + 'px';
        }
    }

    iIntervalId = setInterval(dmove, 2);
}

function $setshrink(targetid) {
    var d = $getform(targetid);
    var h = d.offsetHeight;

    function dmove() {
        h -= 50;//设置层收缩的速度
        if (h <= 0) {
            d.style.display = 'none';
            clearInterval(iIntervalId);
        } else {
            d.style.height = h + 'px';
        }
    }

    iIntervalId = setInterval(dmove, 2);
}

function $spread(targetid, px) {
    var d = $getform(targetid);
    if (d.style.display !== "block") {
        $setspread(targetid, px);
        d.style.display = "none";
    }
    $shrink(targetid);
}

function $shrink(targetid) {
    var d = $getform(targetid);
    if (d.style.display === "block") {
        $setshrink(targetid);
        d.style.display = "none";
    }
}

function $getSum(index) {
    var trlen = $("#addtb tr").length;
    var sum = 0;
    for (i = 1; i < trlen; i++) {
        var val = $.trim($("#addtb tr").eq(i).find("input").eq(index).val());
        sum = sum + parseFloat(val == "" ? "0" : val);
    }
    return sum;
}

function $getBool() {
    var bool = false;
    var trlen = $("#addtb tr").length;
    var sum = 0;
    for (i = 1; i < trlen; i++) {
        var val3 = $.trim($("#addtb tr").eq(i).find("input:eq(1)").val());
        var val4 = $.trim($("#addtb tr").eq(i).find("input:eq(2)").val());
        if (val3 == "" && val4 == "" || val3 != "" && val4 != "") {
            bool = true;
            break;
        }
        if(val3==""){
            $.trim($("#addtb tr").eq(i).find("input:eq(1)").val(" "));
        }
        if(val4==""){
            $.trim($("#addtb tr").eq(i).find("input:eq(2)").val(" "));
        }
    }
    return bool;
}

function $addone() {
    var trlen = $("#addtb tr").length;
    var obj = $("#addtb tr").get(trlen - 1);
    var tr = $(obj);
    tr.after(tr.clone());
    $("#addtb tr").eq(trlen).find("input:eq(0)").val(trlen);
    $("#addtb tr").eq(trlen).find("input:eq(2)").val("");
    $("#addtb tr").eq(trlen).find("input:eq(3)").val("");
}

function $delone() {
    var trlen = $("#addtb tr").length;
    var obj = $("#addtb tr").get(trlen - 1);
    if ($("#addtb tr").length > 3) {
        $(obj).remove();
    }
}

