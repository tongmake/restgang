/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
var checkFlag = { 
                 bondcd   : false,
                checkState: "0"  //债券代码复核标识　1复核　２未复核
            };
function getBondName(bondcdId,cpath){ 
                var bondcd = $("#"+bondcdId+"").val(); 
                $("#yrstomtrty").val("");
                if(bondcd.length===0){
                    return false;
                }
                checkFlag.bondcd     = false;
                checkFlag.checkState = "0";
                
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
                                $("#bdshrtnm").val(""); 
                                alert("该债券代码未复核！");
                            }else{
                                checkFlag.bondcd=true;
                                checkFlag.checkState = "1";
				$("#bdshrtnm").val(data.bondshortnm); 
                                if($("#valtndt_date").val()!==""){
                                    getYear("valtndt_date",bondcdId,cpath);
                                }
                            }
			},
                       error: function() { 
                        checkFlag.bondcd=false;
                        checkFlag.checkState = "0";
                        alert("查询数据失败！");
                        $("#bdshrtnm").val(""); 
                    }
		});
	    }
function getYear(dateId,bondcdId,cpath){
    var bondcd = $("#"+bondcdId+"").val(); 
    var dateStr = $("#"+dateId+"").val();
    if(checkFlag.bondcd){
        $("#yrstomtrty").val("");
       // alert(obj.value);  
      //  alert(dateStr);
        $.ajax({
                type : 'POST',
                contentType : 'application/text',
                url :  cpath+'/bizdata/getbondPer?bondcd='+bondcd+"&valDateStr="+dateStr,
                data : {
                    "bondcd":bondcd,
                    "valDateStr":dateStr
                }, 
                success : function(data) { 
                   // alert("查询数据！"+data);
                    $("#yrstomtrty").val(data);
                },
               error: function() { 
                 
                 alert("查询数据失败！");
            }
        });
    }
    
}
