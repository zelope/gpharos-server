// 15분(900,000 밀리초)마다 페이지를 새로고침
setInterval(function(){
    location.reload();
}, 400000); // 15분 = 900,000 밀리초

// 새로고침 버튼 동작
document.getElementById('refresh-button').onclick = function() {
    location.reload();  // 페이지 새로고침
};
