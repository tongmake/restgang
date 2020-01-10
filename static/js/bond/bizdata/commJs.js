/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
var checkFlag = {
                "hasNull" : false, //非空检查
                "number"  : false,
                 bondcd   : false,
                checkState: "0"  //债券代码复核标识　1复核　２未复核
            };

          
          //获取债券信息
            function getBondInfo(bondcdId,cpath){ 
                var bondcd = $("#"+bondcdId+"").val();
                //alert(bondcd);
                checkFlag.bondcd=false;
		//alert(bondcd);
                if(bondcd.length===0){
                    return false;
                }
		$.ajax({
			type : 'POST',
			contentType : 'application/text',
			url :  cpath+'/bizdata/getbondinfo',
			data : bondcd,
			dataType : 'json',
			success : function(data) { 
                            //alert(data);
                            if(data.checkstate!=='1'){
                                checkFlag.bondcd=true;
                                checkFlag.checkState = "2";
                                $("#bondshortnm").val("");
                                $("#bonddepositplaceno").val("");
                                $("#bonddepositplace").val("");
                                $("#nominalrate").val("");
                                $("#issuer").val("");
                                alert("该债券代码未复核！");
                            }else{
                                checkFlag.bondcd=true;
                                checkFlag.checkState = "1";
				$("#bondshortnm").val(data.bondshortnm);
                                $("#bonddepositplaceno").val(data.bonddepositplace);
                                $("#bonddepositplace").val(data.bonddepositplaceZh);
                                $("#nominalrate").val(data.nominalrate);
                                $("#issuer").val(data.issuer);
                            }
			},
                       error: function() { 
                        checkFlag.bondcd=false;
                        checkFlag.checkState = "0";
                        alert("查询数据失败！");
                        $("#bondshortnm").val("");
                        $("#bonddepositplaceno").val("");
                        $("#bonddepositplace").val("");
                        $("#nominalrate").val("");
                        $("#issuer").val("");
                    }
		});
	    }
//加法
function accAdd(arg1, arg2) {
    var r1, r2, m;
    try {
        r1 = arg1.toString().split(".")[1].length;
    } catch (e) {
        r1 = 0;
    }
    try {
        r2 = arg2.toString().split(".")[1].length;
    } catch (e) {
        r2 = 0;
    }
    m = Math.pow(10, Math.max(r1, r2)+1);//返回 10 的 y 次幂
    return (arg1 * m + arg2 * m) / m;
}
//乘法
function accMul(arg1, arg2)
{
    var m = 0, s1 = arg1.toString(), s2 = arg2.toString();
    try {
        m += s1.split(".")[1].length;
    } catch (e) {
    }
    try {
        m += s2.split(".")[1].length;
    } catch (e) {
    }
    return Number(s1.replace(".", "")) * Number(s2.replace(".", "")) / Math.pow(10, m);
} 
//除法
function accDiv(arg1, arg2)
{
    var m = 0, s1 = arg1.toString(), s2 = arg2.toString();
    try {
        m += s1.split(".")[1].length;
    } catch (e) {
    }
    try {
        m += s2.split(".")[1].length;
    } catch (e) {
    }
    return Number(s1.replace(".", "")) / Number(s2.replace(".", "")) / Math.pow(10, m);
} 
     //小数点后两位小数
     function checkNumEmpty(obj) {
         var no = "";
         if(obj.value == ""){
             obj.value = "";
             return true;
         }
         if(obj.value.indexOf('\.') ==(obj.value.length-1) && obj.value.indexOf('\.')>0){
              no += obj.value;
             return ture;
         }
        if((/^\d+(\.\d{2})?$/.test(obj.value))||(/^\d+(\.\d{1})?$/.test(obj.value))){
              no += obj.value;
         }
         obj.value =no;
     }
     function checkNum(obj) {
         if(''!= obj.value.replace(/\d{1,}\.{0,1}\d{0,2}/,'')){
                 obj.value = obj.value.match(/\d{1,}\.{0,}\d{0,2}/) ==null ? '':obj.value.match(/\d{1,}\.{0,1}\d{0,2}/);
         }
     }
     function checkNum4(obj) {
         if(''!= obj.value.replace(/\d{1,}\.{0,1}\d{0,4}/,'')){
                 obj.value = obj.value.match(/\d{1,}\.{0,}\d{0,4}/) ==null ? '':obj.value.match(/\d{1,}\.{0,1}\d{0,4}/);
         }
     }
     function checkMoney0(obj) {
         //数字，千位分隔样式，小数点后限长2位
        var reg0 =/^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/;
         var reg = /(\d+)(,\d{0,3})*(\.\d{0,2})?/;
         if(''!= obj.value.replace(reg,'')){
                 alert("ok");
                 obj.value = obj.value.match(reg)==null  ? '':obj.value.match(reg);
         }
     }
      function checkMoney(obj) {
         if(''!= obj.value.replace(/(\d*)(,\d{0,3})*(\.\d{0,2})?/,'')){
                 obj.value = obj.value.match(/(\d*)(,\d{0,3})*(\.\d{0,2})?/) ==null ? '':obj.value.match(/(\d*)(,\d{0,3})*(\.\d{0,2})?/);
         }
     }
