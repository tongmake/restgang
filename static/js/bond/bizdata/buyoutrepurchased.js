var checkFlag = {
    bondcd: false,
    checkState: "1"  //债券代码复核标识　1复核　２未复核
};
//非空项检查
function bcheckNull() {
    var x = $("#accountdate1_date").val().split("-");
    var z = $("#transactiondate").val().split("-");
    var accountratecd = $("#accountratecd").val();
    var dt1 = new Date();
    var dt3 = new Date();
    dt1.setFullYear(x[0]);
    dt1.setMonth(x[1] - 1);
    dt1.setDate(x[2]);
    dt3.setFullYear(z[0]);
    dt3.setMonth(z[1] - 1);
    dt3.setDate(z[2]);
    var dif2 = (dt1.getTime() - dt3.getTime()).toFixed(0);
    if ((dif2 <= 0 && accountratecd === "1") || (dif2 > 0 && accountratecd === "0")) {
        alert("请选择正确的清算速度");
        return false;
    }
    if (document.getElementById("bondcd").value === "") {
        alert("债券代码不能为空");
        return false;
    }
    if (document.getElementById("repurchaseperiod").value === "") {
        alert("回购期限不能为空");
        return false;
    }
    if (document.getElementById("counterparty").value === "") {
        alert("对手方名称不能为空");
        return false;
    }
    if (document.getElementById("repurchasedirection").value === "") {
        alert("回购方向不能为空");
        return false;
    }
    if (document.getElementById("accountdate1_date").value === "") {
        alert("首期交割日期不能为空");
        return false;
    }
    if (document.getElementById("accountdate2_date").value === "") {
        alert("到期交割日期不能为空");
        return false;
    }
    if (document.getElementById("actualreservesdays").value === "") {
        alert("实际占款天数不能为空");
        return false;
    }
    if (document.getElementById("repurchaserate").value === "") {
        alert("回购利率不能为空");
        return false;
    }
    if (document.getElementById("aggtfaceamt").value === "") {
        alert("券面总额不能为空");
        return false;
    }
    if (document.getElementById("netprice1").value === "") {
        alert("首期交易净价不能为空");
        return false;
    }
    if (document.getElementById("acrdintrst1").value === "") {
        alert("首期应计利息不能为空");
        return false;
    }
    if (document.getElementById("price1").value === "") {
        alert("首期交易全价不能为空");
        return false;
    }
    if (document.getElementById("settlmamt1").value === "") {
        alert("首期结算金额不能为空");
        return false;
    }
    if (document.getElementById("netprice2").value === "") {
        alert("到期交易净价不能为空");
        return false;
    }
    if (document.getElementById("acrdintrst2").value === "") {
        alert("到期应计利息不能为空");
        return false;
    }
    if (document.getElementById("price2").value === "") {
        alert("到期交易全价不能为空");
        return false;
    }
    if (document.getElementById("settlmamt2").value === "") {
        alert("到期结算金额不能为空");
        return false;
    }
    return true;
}

function bcheckNumber() {
    var x = document.getElementById("repurchaserate").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("回购利率输入错误！");
        return false;
    }
    x = document.getElementById("settlmamt1").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("首期结算金额输入错误！");
        return;
    }
    x = document.getElementById("settlmamt2").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("到期结算金额输入错误！");
        return;
    }
    x = document.getElementById("aggtfaceamt").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("券面总额输入错误！");
        return;
    }
    return true;
}

function setDay() {
    if ($("#accountdate1_date").val() !== null && $("#accountdate1_date").val() !== "" && $("#accountdate2_date").val() !== null && $("#accountdate2_date").val() !== "") {
        var x = $("#accountdate1_date").val().split("-");
        var y = $("#accountdate2_date").val().split("-");
        var z = $("#transactiondate").val().split("-");
        var repurchaseperiod = $("#repurchaseperiod").val();
        var dt1 = new Date();
        var dt2 = new Date();
        var dt3 = new Date();
        //首期交割日期
        dt1.setFullYear(x[0]);
        dt1.setMonth(x[1] - 1);
        dt1.setDate(x[2]);
        //到期交割日期
        dt2.setFullYear(y[0]);
        dt2.setMonth(y[1] - 1);
        dt2.setDate(y[2]);
        //交易日期
        dt3.setFullYear(z[0]);
        dt3.setMonth(z[1] - 1);
        dt3.setDate(z[2]);
        //到期交割日期-首期交割日期
        var dif = (dt2.getTime() - dt1.getTime()).toFixed(0);
        var days = dif / (24 * 60 * 60 * 1000);
        //首期交割日期-交易日期
        var dif2 = (dt1.getTime() - dt3.getTime()).toFixed(0);
        var days2 = dif2 / (24 * 60 * 60 * 1000);
        if (days2 < 0) {
            $("#accountdate1_date").val("");
            alert("请选择正确的首期交割日期");
            return;
        }
        if (days > 0) {
            $("#actualreservesdays").val(days);
        } else {
            //校验
            $("#actualreservesdays").val("");
            $("#accountdate1_date").val("");
            $("#accountdate2_date").val("");
            alert("请选择正确日期");
            return;

        }
        if (repurchaseperiod !== null && repurchaseperiod > days) {
            $("#repurchaseperiod").val("");
            alert("请输入正确的回购期限值");
            return;
        }
    }
}
function setNum() {
    var netprice1 = $("#netprice1").val();//首期交易净价
    var settlmamt1 = $("#settlmamt1").val();//首期结算金额
    var acrdintrst1 = $("#acrdintrst1").val();//首期应计利息
    var aggtfaceamt = $("#aggtfaceamt").val();//券面总额

    var netprice2 = $("#netprice2").val();//到期交易净价
    var settlmamt2 = $("#settlmamt2").val();//首期结算金额
    var acrdintrst2 = $("#acrdintrst2").val();//首期应计利息
    if (netprice1 !== "" && aggtfaceamt !== "") {
        var temp1 = netprice1 * aggtfaceamt * 100;
        var result1 = temp1.toFixed(2);
        $("#netpriceamt1").val(result1);//首期净价金额
    }
    if (settlmamt1 !== "") {
        var netpriceamt1 = $("#netpriceamt1").val();
        var temp = settlmamt1 - netpriceamt1;
        $("#acrdintrstamt1").val(temp);
        $("#priceamt1").val(settlmamt1);//首期全价金额
    }
    if (netprice1 !== "" && acrdintrst1 !== "") {
        var temp = Number(netprice1) + Number(acrdintrst1);
        $("#price1").val(temp.toFixed(4));//首期交易全价
    }


    if (netprice2 !== "" && aggtfaceamt !== "") {
        var temp = netprice2 * aggtfaceamt * 100;
        $("#netpriceamt2").val(temp.toFixed(2));//到期净价金额
    }

    if (settlmamt1 !== "") {
        var netpriceamt2 = $("#netpriceamt2").val();
        var temp = settlmamt2 - netpriceamt2;
        $("#acrdintrstamt2").val(temp);
        $("#priceamt2").val(settlmamt2);//到期全价金额
    }
    if (netprice2 !== "" && acrdintrst2 !== "") {
        var temp = Number(netprice2) + Number(acrdintrst2);
        $("#price2").val(temp.toFixed(4));//到期交易全价
    }
}
//获取债券信息
function BondInfo(cpath) {
    var bondcd = $("#bondcd").val();
    checkFlag.bondcd = false;
    //alert(bondcd);
    if (bondcd.length === 0) {
        return false;
    }
    $.ajax({
        type: 'POST',
        contentType: 'application/text',
        url: cpath + '/bizdata/getbondinfo',
        data: bondcd,
        dataType: 'json',
        success: function (data) {
            //alert(data);
            if (data.checkstate !== '1') {
                checkFlag.bondcd = true;
                checkFlag.checkState = "2";
                $("#bondshortnm").val("");
                $("#bonddepositplaceno").val("");
                $("#bonddepositplace").val("");
                $("#nominalrate").val("");
                alert("该债券代码未复核！");
            } else {
                checkFlag.bondcd = true;
                $("#bondshortnm").val(data.bondshortnm);
                $("#bonddepositplaceno").val(data.bonddepositplace);
                $("#bonddepositplace").val(data.bonddepositplaceZh);
                $("#nominalrate").val(data.nominalrate);
            }
        },
        error: function () {
            alert("债券代码输入有误！");
            $("#bondshortnm").val("");
            $("#bonddepositplaceno").val("");
            $("#bonddepositplace").val("");
            $("#nominalrate").val("");
        }
    });
}

