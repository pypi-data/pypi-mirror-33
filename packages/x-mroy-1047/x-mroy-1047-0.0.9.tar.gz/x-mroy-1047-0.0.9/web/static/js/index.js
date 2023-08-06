function JsonPost(url, data, callback){
    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: function( data ) {
            console.log(data);
            if (callback != null){
                callback(data);
            }
        },
        dataType: 'json'
    });
}

function JsonGet(url, callback){
    $.getJSON(url, callback);
}




