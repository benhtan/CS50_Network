console.log('script running')

document.addEventListener('DOMContentLoaded', function() {
    follow_unfollow_btn = document.querySelector('#follow_unfollow_btn');
    if (follow_unfollow_btn === null) {
        console.log('follow_unfollow_btn not found')
    } else {
        follow_unfollow_btn.innerHTML = follow_unfollow_btn_text();
        follow_unfollow_btn.onclick = follow_unfollow;
    }

});

function follow_unfollow_btn_text() {
    return 'Follow/Unfollow'
}

function follow_unfollow() {
    console.log('follow/unfollow button clicked')
}