$('document').ready(function(){ 
var tracksss= document.getElementById('TRACK').innerText;
      $('.fa-hand-o-down').hide();
       $('#pub2').hide(); 
      

       
     $('#feedback').click(function(){

    
    var email = 'thang.doan@mail.mcgill.ca';
        var subject = 'music recommendations';
        var emailBody = 'your feedback or comments';
        var attach = 'path';
        document.location = "mailto:"+email+"?subject="+subject+"&body="+emailBody+
            "?attach="+attach;


  });
     
      $('#submit').click(function(){
        
        if($('.rating').val()>0){

       $('#rating3').hide();
        
        console.log('hide');
        $.ajax({
      type: "POST",
      url:"/save_rating",  
      async : false,
     data: { rating: $('.rating').val(),  
   wordcloud: $('#tokenfield').val(), track_pseudo:tracksss},  
     dataType: 'json',
     success:function(jsons){

      var data = JSON.stringify(jsons);
        var data2=JSON.parse(data);   
        alert('Thanks for your comment !'); 


     },
     error: function(){
      alert('error during the callback');
     },
    });
   }else{
    alert('please give a rating !');
   }

 });
  



});


// function for getting back the length of the song
/////////////////////////////////////
var time = document.getElementById("myAudio");
  
  function getCurTime() { 
       alert((time.currentTime/length.duration)*100);   
         
      // $('#lol2').text(time.currentTime); 
       //$('#listening_time').text(time.currentTime); 
       
  }

  var length = document.getElementById("myAudio");

  var l=length.duration;
  function myFunction() { 
    alert(length.duration);
} 

function update(player) {

    var duration = player.duration;    // Durée totale

    var time     = player.currentTime; // Temps écoulé

    var fraction = time / duration;
    var percent  = Math.ceil(fraction * 100);
 
    $('.listening_time').val(time);
    $('.percentage').val(fraction); 
    $('.listening_time2').val(time);
    $('.percentage2').val(fraction); 
    $('.time_before_rated').val(time);

    //$('.percentage').each(function(){
    //  $(this).val(fraction);
    //});
};

///////////////// text lyrics

  

// rating
/////////////////////////

 $(function () { 
       $('.rating').rating();           
       
        $('.rating').on('change', function () {
           $('#heart-rate').text($(this).val());
        });        
  });

 

 // token list
 ///////////////////

var mot=[];

$(function () { 
//console.log('1');
$.ajax({
    type: "GET",

    url:"/static/list/token_list.csv",
    
    dataType: "text",
    async : false,
   success: function(text){parseTxt(text);},
   error: function(){
    alert('can t open file or doesn t exist');
   },
   });
 //alert('2');
// console.log('2');
 function parseTxt(text){
  //alert('success');

  var rows=text.split('\n'); 
  //console.log(rows);

  $.each(rows, function( index, value ) {
    
    mot[index]=value.replace(' ','');
   
  });
  
  
  };

$('#tokenfield').tokenfield({

  autocomplete: {
    source:mot,
    delay: 100
  },
  showAutocompleteOnFocus: true


});

$('#tokenfield').on('tokenfield:createtoken', function (event) {
    var existingTokens = $(this).tokenfield('getTokens');
    $.each(existingTokens, function(index, token) {
        if (token.value === event.attrs.value) 
                    event.preventDefault();
    });
});

$('#tokenfield').on('tokenfield:createtoken', function (event) {
  //console.log(mot);
   
    var exists = false;
    $.each(mot, function( index, value ) {
            //console.log(value+","+event.attrs.value);

             // if (value.replace('\r', '')==String(event.attrs.value)) {
              if (value.replace(' ','')==String(event.attrs.value)) {
     
               exists = true;
          
               
            
            }
          
                   
    });
    if(exists === false)
        event.preventDefault();
      // console.log(exists);
      // console.log(mot[16]);
});

       

});
