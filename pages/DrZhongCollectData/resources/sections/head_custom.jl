add!(p_head, HtmlConstructor.JS"""
// 将内容变成文件下载
// ------------------------------------------------------
var funDownload = function (content, filename) {
    // 创建隐藏的可下载链接
    var eleLink = document.createElement('a');
    eleLink.download = filename;
    eleLink.style.display = 'none';
    // 字符内容转变成blob地址
    var blob = new Blob([content]);
    eleLink.href = URL.createObjectURL(blob);
    // 触发点击
    document.body.appendChild(eleLink);
    eleLink.click();
    // 然后移除
    document.body.removeChild(eleLink);
};
//  form生成json字符串
// ------------------------------------------------------
function onSubmit(form) {
    // 序列化为json的pair数组{name:,value:}
    var jsondata = $(form).serializeArray();
    // 将json变为纯字符串
    var data = JSON.stringify(jsondata);

    // pick up "faculty name + university"组成文件名
    var FileName = document.getElementById("FacultyFirstName").value + "_" + document.getElementById("FacultyLastName").value + "_" + document.getElementById("FacultyCurrentUniversity").value + ".json";

    // 生成json下载文件
    funDownload(data, FileName)

    // console.log(data);
    return false; // return a false to prevent submit
};
""")

















#
