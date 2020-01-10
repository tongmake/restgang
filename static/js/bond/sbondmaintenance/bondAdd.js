/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

function checkForm(){
                        var bondcd          = $("#bondcd");//债券代码
                        var bondshortnm     = $("#bondshortnm");//债券简称
                        var zjbp            = $("#zjbp");//债券品种：
                        var fxfs            = $("#fxfs");   //付息方式：
                        var bonddepositplace= $("#bonddepositplace") ;//托管场所
                        var issuer          = $("#issuer"); //发行人：
                        var issuerdate_date = $("#issuerdate_date");//发行日
                        var valuedate_date  = $("#valuedate_date");//起息日：
                        var duedate_date    = $("#duedate_date"); //到期日
                        var maturityvalue   = $("#maturityvalue"); //债券期限数值：
                        var periodunit      = $("#periodunit");//债券期限单位
                        var interestref     = $("#interestref");//计息基准
                        var listedondate_date= $("#listedondate_date");//上市流通日
                        var issuerprice     = $("#issuerprice");//发行价格
                        var circulation     = $("#circulation");//发行量
                        var remainprincipalval= $("#remainprincipalval");//剩余本金值
                        var currency        = $("#currency");//币种
                        var put_date        = $("#put_date");//首次付息日
                        
                       
                        if(!checkElement(bondcd,"债券代码")){
                            return false;
                        }
                        if(!checkElement(bondshortnm,"债券简称")){
                            return false;
                        }
                        if(!checkElement(zjbp,"债券品种")){
                            return false;
                        }
                        if(!checkElement(fxfs,"付息方式")){
                            return false;
                        }
                        if(!checkElement(bonddepositplace,"托管场所")){
                            return false;
                        }
                        if(!checkElement(issuer,"发行人")){
                            return false;
                        }
                        if(!checkElement(issuerdate_date,"发行日")){
                            return false;
                           }
                        if(!checkElement(valuedate_date,"起息日")){
                            return false;
                           }
                        if(!checkElement(duedate_date,"到期日")){
                            return false;
                           }
                        //到期日应大于发行日,且大于起息日。
                        if(issuerdate_date.val()>duedate_date.val()){
                            alert("到期日应大于发行日");
                            duedate_date.focus();
                            return false;
                        }
                        if(valuedate_date.val()>duedate_date.val()){
                            alert("起息日应小于等于到期日");
                            valuedate_date.focus();
                            return false;
                        }
                        if(listedondate_date.val()!=""){
                            if(listedondate_date.val()>duedate_date.val()){
                                alert("到期日应大于上市流通日");
                                duedate_date.focus();
                                return false;
                            }
                            if(issuerdate_date.val()>listedondate_date.val()){
                                alert("上市流通日应大于发行日");
                                listedondate_date.focus();
                                return false;
                             }
                        }
                        if(!checkElement(interestref,"计息基准")){
                            return false;
                        }
                          //债券品种
                        if(zjbp.val() == "B10"){
                            if(!checkElement(put_date,"首次付息日")){
                            return false;
                           }
                        //且起息日<=首次付息日<=到期日
                        //alert(valuedate_date.val()+" "+duedate_date.val());
                        if(valuedate_date.val()>put_date.val()){
                            alert("起息日应小于等于首次付息日");
                             valuedate_date.focus();
                            return false;
                           }
                        if(put_date.val()>duedate_date.val()){
                            alert("首次付息日应小于等于到期日");
                            put_date.focus();
                            return false;
                           }
                        }
                        //不同的付息方式校验数据
                        if(!checkFxfs()){
                            return false;
                        }
                        if(!checkElement(issuerprice,"发行价格")){
                            return false;
                        }else{
                            if(Number(issuerprice.val())===0){
                                alert("发行价格不能为0");
                                return false;
                            }
                            if(Number(issuerprice.val())<0){
                                alert("发行价格大于０");
                                return false;
                            }
                        }
                        if(!checkElement(circulation,"发行量")){
                            return false;
                        }else{
                            if(Number(circulation.val())===0){
                                alert("发行量不能为0");
                                return false;
                            }
                            if(Number(circulation.val())<0){
                                alert("发行量大于０");
                                return false;
                            }
                        }
                        if(!checkElement(remainprincipalval,"剩余本金值")){
                            return false;
                        }
                        if(!checkElementCanNoInput()){
                            return false;
                        }
                        return true;
                    }
                    //可不输入元素提示
                    function checkElementCanNoInput(){
                        var bondcreditrat   = $("#bondcreditrat");//债券信用评级
                        var maincreditrat   = $("#maincreditrat");//主体信用评级：
                        var lnlinerat       = $("#lnlinerat");//行内评级
                        var pyatyiclassify  = $("#pyatyiclassify");//五级分类
                        var sinkingsequence = $("#sinkingsequence");//偿债次序
                        var directional     = $("#directional");//是否定向
                        var firstpayment    = $("#firstpayment");//债券风险权重
                        var title           = "";
                        var splitFlag       = false;
                        var inputObj  ;
                        //G．若债券信用评级、主体信用评级、行内评级、五级分类、偿债次序、是否定向、债券风险权重用户没有输入，就直接点了保存，
                        //则提示用户未输入XX要素，是否继续保存？保存/返回。
                        if(bondcreditrat.val()==""){
                            splitFlag = true;
                            title += "债券信用评级";
                            
                        }
                        if(maincreditrat.val()=="" ){
                            if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "主体信用评级";
                            inputObj = maincreditrat;
                        }
                       if(lnlinerat.val()=="" ){
                            if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "行内评级";
                            inputObj = lnlinerat;
                           
                        }
                        if(pyatyiclassify.val()=="" ){
                             if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "五级分类";  
                            inputObj = pyatyiclassify;
                        }
                        if(sinkingsequence.val()=="" ){
                            if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "偿债次序";   
                            inputObj = sinkingsequence;
                        }
                        if(directional.val()=="" ){
                            if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "是否定向";  
                            inputObj = directional;
                            
                        }
                        if(firstpayment.val()=="" ){
                            if(splitFlag){
                                title+=",";
                            }
                            splitFlag =  true;
                            title += "债券风险权重"; 
                            inputObj = firstpayment;
                            
                        } 
                        //有未输入的要素
                        if(splitFlag){
                            if(!confirm("未输入"+title+"要素，是否继续保存？")){
                                inputObj.focus();
                                return false;
                            }
                        }
                        
                        return true;
                    }
                    function checkFxfs(){
                        var nominalrate     = $("#nominalrate");//票面利率
                        var fxfs            = $("#fxfs");   //付息方式
                        var currentbaserate  = $("#currentbaserate");//当期基础利率
                        var irexcs          = $("#irexcs");//基本利差：
                        var bstrtype        = $("#bstrtype");//基准利率种类
                        var interestpaymentcycle= $("#interestpaymentcycle");//付息周期：
                         //alert(fxfs.val());
                         if(!checkElement(interestpaymentcycle,"付息周期")){
                                return false;
                            }
                        if ( fxfs.val() == "2"  ) { 
                            //附息式浮动利率  当期基础利率、基本利差、基准利率种类为必输项，票面利率置灰不允许输入
                            if(!checkElement(currentbaserate,"当期基础利率")){
                              return false;
                            }
                            if(Number(currentbaserate.val())<0){
                                alert("当期基础利率大于等于０");
                                currentbaserate.focus();
                            }
                             if(!checkElementZero(irexcs,"基本利差")){
                                return false;
                            }else{
                                if(Number(irexcs.val())===0){
                                alert("基本利差不能为0");
                                return false;
                                }
                                 if(Number(irexcs.val())<0){
                                alert("基本利差应大于0");
                                return false;
                                }
                            }
                             if(!checkElement(bstrtype,"基准利率种类")){
                                return false;
                            }
                            if(!checkElementZero(nominalrate,"票面利率")){
                                return false;
                            }else{
                                if(Number(nominalrate.val())<=0){
                                    alert("票面利率应大于0");
                                    return false;
                                  }
                            }
                        }else if(fxfs.val()  === "1"){
                            //附息式固定利率 当期基础利率、基本利差、基准利率种类置灰不允许输入
                            if(!checkElementZero(nominalrate,"票面利率")){
                                return false;
                            }else{
                                 if(Number(nominalrate.val())<=0){
                                    alert("票面利率应大于0");
                                    return false;
                                  }
                            }
                        }else if(fxfs.val()  === "0"){
                            //利随本清 当期基础利率、基本利差、基准利率种类置灰不允许输入
                            if(!checkElementZero(nominalrate,"票面利率")){
                                return false;
                            }else{
                                if(Number(nominalrate.val())<=0){
                                    alert("票面利率应大于0");
                                    return false;
                                  }
                            }
                        }
                        return true;
                        
                    }
                    function checkElementZero(el,txt){
                        if(el.val()==""){
                            alert(txt+"要素未输入");
                            el.focus();
                            return false;
                        }else{
                            if(Number(el.val())===0){
                                alert(txt+"要素不能为０");
                                el.focus();
                            }else{
                               return true;    
                            }
                            
                        }
                    }
                    function checkElement(el,txt){
                        if(el.val()==""){
                            alert(txt+"要素未输入");
                            el.focus();
                            return false;
                        }else{
                            return true;
                        }
                    }
                    window.onload = function() {
                            var select = document.getElementById("bp");
                            var put = document.getElementById("put_date");//首次付息日
                            //当债券品种选择的不是资产支持证券，则“首次付息日”要素置灰不允许输入。
                            if (select.value == "B10"){//B10 资产支持证券
                                put.readOnly = false;
                            } else {
                                put.readOnly = true;
                                put.value = "";
                            }
                        }
           
                    $.fn.serializeObject = function() {
                        var o = {};
                        var a = this.serializeArray();
                        $.each(a, function() {
                            if (o[this.name]) {
                                if (!o[this.name].push) {
                                    o[this.name] = [o[this.name]];
                                }
                                o[this.name].push(this.value || '');
                            } else {
                                o[this.name] = this.value || '';
                            }
                        });
                        return o;
                    };
                    
                    
                    function chbd() {
                        var fxfs            = $("#fxfs").val();
                        var currentbaserate = $("#currentbaserate");//当期基础利率
                        var irexcs          = $("#irexcs");//基本利差
                        var bstrtype        = $("#bstrtype");//基准利率
                        var nominalrate     = $("#nominalrate") ;//票面利率
                        var interestpaymentcycle = $("#interestpaymentcycle");//付息周期
//                        alert("付息方式值"+fxfs);
                        //附息式浮动利率 
                        if ( fxfs === "2"  ) { 
                            //附息式浮动利率  当期基础利率、基本利差、基准利率种类为必输项，票面利率置灰不允许输入
                            //票面利率= 当期基础利率 + 基本利差
                            var aa = $("#irexcs").val();//基本利差(%)
                            var bb =$("#currentbaserate").val();//当期基础利率(%)
                            $("#nominalrate").val(Number(aa) +Number(bb));
                            setReadonly(nominalrate); 
                            setDisplay(currentbaserate);
                            setDisplay(irexcs);
                            setDisplay(bstrtype);
                            setDisplay(interestpaymentcycle);
                            //interestpaymentcycle.attr("value","");
                            $(".changByFxfs").show();   //必输项显示  //必输项控制 加类
                        }else if(fxfs == "3" || fxfs == "4"){
                            //当付息方式选择“贴现式”或“零息式”时，票面利率、当期基础利率、基本利差、基准利率种类置灰不允许输入，票面利率为０
                              setReadonly(nominalrate);
                              setDisable(currentbaserate);
                              setDisable(irexcs);
                              setDisable(bstrtype);
                            //“付息周期”要素默认为：到期还本付息，不允许修改
                            setDisable(interestpaymentcycle);
                            interestpaymentcycle.attr("value","0");
                            nominalrate.attr("value","0");
                             $(".changByFxfs").hide();
                        }else if(fxfs == "1"){
                            //附息式固定利率 当期基础利率、基本利差、基准利率种类置灰不允许输入
                            setDisable(currentbaserate);
                            setDisable(irexcs);
                            setDisable(bstrtype);
                            setDisplay(nominalrate);
                            setDisplay(interestpaymentcycle);
                            //interestpaymentcycle.attr("value","");
                            $(".changByFxfs").hide();
                        }else if(fxfs == "0"){
                            //利随本清 当期基础利率、基本利差、基准利率种类置灰不允许输入
                            setDisable(currentbaserate);
                            setDisable(irexcs);
                            setDisable(bstrtype);
                            setDisplay(nominalrate);
                             //“付息周期”要素默认为：到期还本付息，不允许修改
                            setDisable(interestpaymentcycle);
                            interestpaymentcycle.attr("value","0");
                           
                            $(".changByFxfs").hide();
                        }
                    }
                 function setDisplay(el){
                     //el.val("");
                    if(el.attr("readonly")=="readonly"){
                     el.removeAttr("readonly");
                    }
                    if(el.attr("disabled")){
                     el.removeAttr("disabled");
                    }
                 }
                 //控件置灰
                 function setDisable(el){
                     el.val("");
                     el.attr("disabled", "true"); 
                    
                 }
                 function setReadonly(el){
                     el.val("");
                     el.attr("readonly", "true"); 
                    
                 }
            function setNomilate(){
                //付息方式为付息式浮动利率 ，票面利率= 当期基础利率 + 基本利差
                var fxfs            = $("#fxfs").val();
                if(fxfs==="2"){
                var aa = $("#irexcs").val();//基本利差(%)
                var bb =$("#currentbaserate").val();//当期基础利率(%)
                $("#nominalrate").val(accAdd((aa) ,(bb)));
            }
            }
            function checkNum(obj) {
                 //检查是否是非数字值
                if (isNaN(obj.value)) {
                    obj.value = "";
                }
                if (obj != null) {
                    //检查小数点后是否对于两位
                    if (obj.value.toString().split(".").length > 1 && obj.value.toString().split(".")[1].length > 2) {
                        alert("小数点后多于两位！");
                        obj.value = "";
                    }
                }
            
            }
