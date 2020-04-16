//リクエストパラメーターのセット
const KEY = 'AIzaSyBx2MnaLGcVlLaG5NFSXTNOgr5lD-21-_k' ;// APIKEY
const ID = 'bKzlm45wTu0' ;// 動画ID
let url = 'https://www.googleapis.com/youtube/v3/videos'; // APIURL
url += '?id=' + ID;
url += '&key=' + KEY;
url += '&part=snippet,contentDetails,statistics,status';

//https://www.googleapis.com/youtube/v3/videos?id=bKzlm45wTu0&key=AIzaSyBx2MnaLGcVlLaG5NFSXTNOgr5lD-21-_k&part=snippet,contentDetails,statistics,status

//Ajax通信をする
$(function(){
  $.ajax({
    url: url,
    dataType : 'json'
  }).done(function(data){
    // URL
    $('#js-youtube-link').attr('href', `https://www.youtube.com/watch?v=bKzlm45wTu0&t=25s${data.items[0].snippet.channelId}`);

    // サムネイル
    $('#js-youtube-image').attr('src', data.items[0].snippet.thumbnails.medium.url);

    // タイトル
    $('#js-youtube-title').append(data.items[0].snippet.title);

    // チャンネル名
    $('#js-youtube-channel').append(data.items[0].snippet.channelTitle);

    // チャンネルURL
	const $youtubeChannel = $('#js-youtube-channel');
    $youtubeChannel.attr('data-href', `https://www.youtube.com/channel/${data.items[0].snippet.channelId}`);

    // aタグ内で別のURLに遷移
    $youtubeChannel.on('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      window.open($('#js-youtube-channel').data('href'), '_blank');
    });

    // 再生回数
    $('#js-youtube-views').append(data.items[0].statistics.viewCount);

    // 再生時間
    let duration = data.items[0].contentDetails.duration;
    let convertDuration = moment.duration(duration).format('hh:mm:ss');
    $('#js-youtube-duration').append(convertDuration);

    // 投稿日時
    moment.locale('ja');
    let date = data.items[0].snippet.publishedAt;
    let convertDate = moment(date).fromNow();
    $('#js-youtube-date').append(convertDate);

    // 説明
    $('#js-youtube-description').append(data.items[0].snippet.description);

  }).fail(function(data){
    console.log('通信に失敗しました。');
  });
});
