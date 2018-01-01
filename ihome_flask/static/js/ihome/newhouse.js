function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


// 查询地区,设施信息
$.get('/api/v1/house/area_facility',function(data){
    //地区
    var area_html=template('area_list',{area_list:data.area});
    $('#area-id').html(area_html);
    //设施
    var facility_html=template('facility_list',{facility_list:data.facility});
    $('.house-facility-list').html(facility_html)
});
