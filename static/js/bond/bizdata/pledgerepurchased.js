/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
//到期结算金额
function setsettlmamt2() {
    var settlmamt1 = $("#settlmamt1").val();//首期清算金额
    var repurchaserate = $("#repurchaserate").val();//回购利率
    var actualreservesdays = $("#actualreservesdays").val();//实际占款天数
    if (actualreservesdays !== "" && repurchaserate !== "" && settlmamt1 !== "") {
        var temp = settlmamt1 * (1 + repurchaserate / 100 * actualreservesdays / 365);
        var settlmamt2 = temp.toFixed(2);
        $("#settlmamt2").val(settlmamt2);
    }
}
function setDay() {
    if ($("#accountdate1_date").val() !== "" && $("#accountdate1_date").val() !== "" && $("#accountdate2_date").val() !== "" && $("#accountdate2_date").val() !== "") {
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
var checkFlag = {
    "hasNull": false, //非空检查
    "number": false,
};
//非空项检查
function checkNull() {
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
    if (document.getElementById("settlmamt1").value === "") {
        alert("首期结算金额不能为空");
        return false;
    }
    if (document.getElementById("settlmamt2").value === "") {
        alert("到期结算金额不能为空");
        return false;
    }
    return true;
}
function checkchildNull() {
    if (document.getElementById("astypecd").value === "" && document.getElementById("paymentamt").value !== "") {
        alert("资产分类名称不能为空");
        return false;
    }
    if (document.getElementById("pledgefaceamt").value === "") {
        alert("质押面额不能为空");
        return false;
    }
    if (document.getElementById("pledgepropotion").value === "") {
        alert("质押率不能为空");
        return false;
    }
    if (document.getElementById("financeamt").value === "") {
        alert("融资金额不能为空");
        return false;
    }
    if (document.getElementById("bondcd").value === "") {
        alert("债券代码不能为空");
        return false;
    }
    return true;
}

function checkNumber() {
    var x = document.getElementById("repurchaserate").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("回购利率输入错误！");
        return false;
    }
    x = document.getElementById("settlmamt1").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("首期结算金额输入错误！");
        return false;
    }
    x = document.getElementById("settlmamt2").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("到期结算金额输入错误！");
        return false;
    }
    x = document.getElementById("aggtfaceamt").value;
    if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
        alert("券面总额输入错误！");
        return false;
    }
    return true;
}

//维护投组信息，若为正回购，则在持债表中查找可用面额
function getpaymentamt(base) {
    var bondcd = $("#bondcd").val();
    var astypecd = $("#astypecd").val();
    if (bondcd !== null && bondcd !== "" && astypecd !== null && astypecd !== "") {
        var sf = bondcd + "_" + astypecd;
        $.ajax({
            type: 'POST',
            url: base + '/bizdata/pledgefirst/querypaymentamt',
            data: sf,
            success: function (e) {
                $("#paymentamt").val(e);
            }, error: function (e) {
            }
        });
    }
}
function StringToDate(DateStr)
{
    var converted = Date.parse(DateStr);
    var myDate = new Date(converted);
    if (isNaN(myDate))
    {
    //var delimCahar = DateStr.indexOf('/')!=-1?'/':'-';
    var arys= DateStr.split('-');
    myDate = new Date(arys[0],--arys[1],arys[2]);
    }
    return myDate;
} 
Date.prototype.Format = function(fmt) 
        { //author: meizz 
          var o = { 
            "M+" : this.getMonth()+1,                 //月份 
            "d+" : this.getDate(),                    //日 
            "h+" : this.getHours(),                   //小时 
            "m+" : this.getMinutes(),                 //分 
            "s+" : this.getSeconds(),                 //秒 
            "q+" : Math.floor((this.getMonth()+3)/3), //季度 
            "S"  : this.getMilliseconds()             //毫秒 
          }; 
          if(/(y+)/.test(fmt)) 
            fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length)); 
          for(var k in o) 
            if(new RegExp("("+ k +")").test(fmt)) 
          fmt = fmt.replace(RegExp.$1, (RegExp.$1.length===1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length))); 
          return fmt; 
        };

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

