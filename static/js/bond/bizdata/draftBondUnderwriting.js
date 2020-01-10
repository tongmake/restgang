/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


 function calculationRe() {
            //首发时,应计利息金额为0 2015.7.22 首发时，应计利息金额不再为0
                if ($("#whethersecondary").val() === "0") {
                    //首发
                    var paymentaggamt = Number($("#paymentaggamt").val());
                    var consignmentfaceamt =  accMul(Number($("#consignmentfaceamt").val()),10000);//差
                    var y = accAdd(paymentaggamt,-consignmentfaceamt);
          //($("#paymentaggamt").val() - 0 - (remainprincipalval * ($("#consignmentfaceamt").val() - 0) * 10000 / 100)).toFixed(2);
                         $("#premiumdiscountaggamt").val(y);
                         //$("#acrdintrstamt").val("0");
                         //$("#acrdintrstamt").attr("readonly","true");

                }
                if ($("#whethersecondary").val() === "1") {
                    //续发
                    var x = accAdd($("#paymentaggamt").val(), - accMul(Number($("#consignmentfaceamt").val()),10000))
                        x = accAdd(x,-$("#acrdintrstamt").val() );
                    
         //($("#paymentaggamt").val() - 0 - (remainprincipalval * ($("#consignmentfaceamt").val() - 0) * 10000 / 100) - $("#acrdintrstamt").val() - 0).toFixed(2);
                    $("#premiumdiscountaggamt").val(x);   
                    //$("#acrdintrstamt").removeAttr("readonly");
                   // $("#acrdintrstamt").val("");
                    
                }
                getConsignmentprice();
                getAcrdintrst();
            }
            //自动计算承销价格=（缴款总额/承销面额）*100
            function getConsignmentprice(){
                var paymentaggamt = $("#paymentaggamt").val();//缴款总额
                var consignmentfaceamt = $("#consignmentfaceamt").val();//承销面额(万元)
                if(paymentaggamt!==null && paymentaggamt!=="" &&consignmentfaceamt!==null && consignmentfaceamt!==""){
                    
                    consignmentfaceamt = accMul(Number(consignmentfaceamt),10000);
                var divTemp = Number(paymentaggamt)/Number(consignmentfaceamt);
                    divTemp = Math.round(accMul(divTemp,1000000))/1000000;//四舍五入到小数点后6位小数
                // console.info(divTemp);
                $("#consignmentprice").val(accMul(divTemp,100));//数字，小数点前限长3位，小数点后限长4位
                }       
            }
            //自动计算应计利息（元/百元）=应计利息金额（元）/承销面额*100，保留5位小数
            function getAcrdintrst(){
                var acrdintrstamt = $("#acrdintrstamt").val();//应计利息金额
                var consignmentfaceamt = $("#consignmentfaceamt").val();//承销面额
                if(acrdintrstamt!==null && acrdintrstamt!=="" &&consignmentfaceamt!==null && consignmentfaceamt!==""){
                    consignmentfaceamt = accMul(consignmentfaceamt,10000);
                    var t = Math.round(accMul(acrdintrstamt/consignmentfaceamt,10000000))/10000000;//7位小数
                    $("#acrdintrst").val(accMul(t,100));
                  }
            }
            //非空项检查
            function checkNull() {
                if (document.getElementById("bondcd").value === "") {
                    alert("债券代码不能为空");
                    return false;
                }
                if (document.getElementById("paymentdate").value === "") {
                    alert("缴款日期不能为空");
                    return false;
                }
                if (document.getElementById("paymentaggamt").value === "") {
                    alert("缴款总额不能为空");
                    return false;
                }
                if (document.getElementById("acrdintrstamt").value === "") {
                    alert("应计利息金额不能为空");
                    return false;
                }
                if (document.getElementById("acrdintrst").value === "") {
                    alert("应计利息不能为空");
                    return false;
                }
                if (document.getElementById("consignmentprice").value === "") {
                    alert("承销价格不能为空");
                    return false;
                }
                if($("#paymentdate").val()<$("#transactiondateStr").val()){
                    alert("缴款日期应大于等于交易日期");
                    return false;
                }
                if( $("#whethersecondary").val()==="" ){
                     alert("请选择首续发标志名称");
                    return false;
                }
                return true;
            }
            function checkNumber() {
                var x = document.getElementById("paymentaggamt").value;
                if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
                    alert("缴款总额输入错误！");
                    return false;
                }
                x = document.getElementById("acrdintrstamt").value;
                if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
                    alert("应计利息金额输入错误！");
                    return false;
                }
                x = document.getElementById("acrdintrst").value;
                if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
                    alert("应计利息输入错误！");
                    return false;
                }
                x = document.getElementById("consignmentprice").value;
                if (!x.match(/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/)) {
                    alert("承销价格输入错误！");
                    return;
                }
                return true;
            }