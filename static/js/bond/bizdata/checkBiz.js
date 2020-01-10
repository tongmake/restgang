/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
/**
 * ajaxCheckState ,checkForeign 为一组校验,同时校验行外机构,债券代码是否已复核.
 * @param {type} cpath 根路径
 * @param {type} bondcd 债券代码
 * @param {type} orgShortNm 机构简称
 * @param {type} c  回调方法
 * @returns {undefined}
 */
 function ajaxCheckState(cpath,bondcd,orgShortNm,c){ 
             var callBack = c;
		$.ajax({
			type : 'POST',
			contentType : 'application/text',
			url :  cpath+'/bizdata/getbondinfo',
			data : bondcd,
			dataType : 'json',
			success : function(data) {  
                            if(data.checkstate!=='1'){
                                alert("该债券代码未复核！此交易不能复核．");
                            }else{ 
                                 // callBack();
                                 if(orgShortNm===""){
                                     callBack();//复核
                                 }else{
                                     checkForeign(cpath,orgShortNm,c);    
                                 }
                                 
                            }
			},
                       error: function() {
                            alert("查询债券基本资料失败");
                            
                    }
		}); 
            }
//校验行外机构            
  function checkForeign(cpath,orgName,c){
      //alert("校验行外机构!");
      var callBack = c;
      var odbt   = {};
      odbt.counterparty = orgName;
       var jsonmenu = JSON.stringify(odbt);
      $.ajax({
                type : 'POST',
                contentType : 'application/json',
                url :  cpath+'/bizdata/getForeign',
                data: jsonmenu ,
                dataType : 'json',
                success : function(data) {  
                    if(data.checkstate!=='1'){
                        alert("该机构暂未复核！此交易不能复核．");
                    }else{ 
                         callBack();
                    }
                },
               error: function() {
                    alert("行外机构查询失败");
               }
	}); 
  }
  
   
   

