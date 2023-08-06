lis = $("ul.sao-list>li")
for(i=0; i< lis.length; i++){
	l = jQuery(lis[i]);
	console.log(l)

	if (l.has("span").length == 0){
		l.prepend('<span class="glyphicon glyphicon-book"></span>')
	}
}

bts = $("ul.sao-btns").find("button[icon]")
for(i=0; i< bts.length; i++){
	l = bts[i]
	console.log(l)
	icon_name = l.getAttribute("icon");
	$(l).html('<span class="glyphicon glyphicon-'+ icon_name + '"></span>')
}


function wait(id){
  $("a").each(function(e){
    $(e).css("pointer-events", "none")
  })
  $("input").each(function(e){
    $(e).css("pointer-events", "none")
  })

  $("body").css({
    "filter":"blur(15px)"
  })
  if (id != null){
    $(id).css("filter","blur(0px)")
  }
}

function wait_ok(){
  $("body").css({
    "filter":"blur(0px)"
  })
  $("a").each(function(e){
    $(e).css("pointer-events", "")
  })
  $("input").each(function(e){
    $(e).css("pointer-events", "")
  })
  

}


var show_in = function(id, x, y){
    $(id).css({
        "display" : "block",
        "position": "absolute",
        "z-index": 2000,
        "left": x-20,
        "top":y
    })
    $(id).collapse("show");
    open_id = id.slice(1, id.length) + "-opened"
    $(id).attr("id", open_id);

    
}

var change_in = function(id, x, y){
  $(id).css({
    "left": "+=" + x+"px",
    "top":  "+=" + y+"px",
  })
}

function QrGen(data){
  var qrcode = new QRCode("qrcode", {
  text: data,
  width: 260,
  height: 260,
  colorDark: '#efb73e',
  colorLight: "#ffffff"
  });
}

function JsonPost(url, data, callback){
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data),
        success: function( data ) {
            console.log(data);
            wait_ok()
            if (callback != null){
                callback(data);
            }
        },
        dataType: 'json'
    });
    wait()
}

function JsonGet(url, callback){
    $.getJSON(url, callback);
}


var get_width = function(id){
  w = $(id).css("width")
  return w.slice(0, w.length -2)
}

var get_height = function(id){
  w = $(id).css("height")
  return w.slice(0, w.length -2)
}

var close_in = function(id){
  open_id = id + "-opened"
  $(open_id).collapse("hide");
  $(open_id).hide();
  setTimeout(function () {
      $(open_id).attr("id", id.slice(1, id.length));
  }, 1000); 
}

var sao_table = function(id, data){
              // console.log(data);
              console.log("=== some ==")
              table = "<table class=\"table\" ><thead><tr>"
              head = Object.keys(data.data[0])
              for(i=0; i < head.length; i++){
                table += "<th>"+head[i] + "</th>"
              }
              table += "</tr></thead><tbody>"
              for(i = 0; i< data.data.length; i ++){
                item = data.data[i]
                ii = '<tr>'
                for(i2 = 0; i2 < head.length ; i2 ++){
                  ii += '<td>' + item[head[i2]] + '</td>'
                }
                ii += '</tr>'
                table += ii
                // console.log(item)
              }
              table += '</tbody></table>'
              // remove old popover
              $(".sao-list").find("div.popover").remove()
              //init and show
              $(id).popover({
                'content':table,
                'title':'Get Status |pid/port',
                'placement':'right'
              }).popover('show')
              // change some attr  
              $(".sao-list>li>div.popover").css({
                "left": "105%",
                "opacity": "0.9"
              });
              $(".sao-list>li>div.popover>.popover-title").html("<span class='glyphicon glyphicon-envelope' ></span>Get Status");
              $(".sao-list>li>div.popover>.popover-content").html(table);
              // $("#get-status").popover('show')
          }