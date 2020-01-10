/* 
 *交易对手弹出框搜索
 */

          //选择交易对手，返回　数据
          function showCounter(base){
              var url       =  base+"/bizdata/counterSelect";
              //var winPro    = 'dialogHeight:550px;dialogWidth:650px;dialogTop:100px;dialogLeft:300px;center:yes;scrollbars:yes;resizable:1';
              var winPro = 'height=550px, width=600px, top=100,left=200,scrollbars=yes,resizable=1';
            
              var child =  window.open(url, 'newwindow', winPro);   
          }
           
           
          //交易对手托管账号
          function getSforeignmanagementhost(base,counterpartyid){
		//var counterpartyid = $("#h_counterpartyid").val();
		//alert(counterpartyid+"base is "+base+" len is "+base.length);
		$.ajax({
			type : 'POST',
			contentType : 'application/text',
			url :  base+'/bizdata/getSforeignmanagementhostlist',
			data : counterpartyid,
			dataType : 'json',
			success : function(data) {
                                //alert(data.length);
                                createSelect($("#counterpartyescrowacct"),data);
			}
		});
	    }
            
            function createSelect(eObj,eData){
             var option="";
             //alert(eObj.val());
             $("#counterpartyescrowacct").empty();
            $.each(eData,function(key){
                option=option+'<option value ="' +eData[key].escrowacct+ '">' +eData[key].escrowacct+ '</option>';});
            
             $("#counterpartyescrowacct").append(option);
            }

