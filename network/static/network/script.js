console.log('script running')

document.addEventListener('DOMContentLoaded', function() {
    const follow_unfollow_btn = document.querySelector('#follow_unfollow_btn');
    if (follow_unfollow_btn === null) {
        console.log('follow_unfollow_btn not found')
    } else {
        follow_unfollow_btn_text();
        follow_unfollow_btn.onclick = follow_unfollow;
    }

});

//  set the right text for unfollow/follow button
function follow_unfollow_btn_text() {
    // get the username of logged in user
    const logged_in_user = document.querySelector('#logged_in_user').innerHTML;

    // get the username of the profile the logged in user is vieweing
    const user_profile = document.querySelector('#user_profile').innerHTML;

    // get csrf token
    const csrftoken = getCookie('csrftoken');

    // fetch
    fetch('/follow_unfollow', {
        method: 'PUT',
        headers: { "X-CSRFToken": csrftoken },
        body: JSON.stringify({
            logged_in_user: logged_in_user,
            user_profile: user_profile
        })
    })
    .then(response => response.json())
    .then(json => {
        // console.log(json)
        document.querySelector('#follow_unfollow_btn').innerHTML = json.follow_unfollow_btn_text
    })
    .catch(error => {
        console.log('Error: ', error);
    });
}

function follow_unfollow() {
    console.log('follow/unfollow button clicked')
    // get the username of logged in user
    const logged_in_user = document.querySelector('#logged_in_user').innerHTML;

    // get the username of the profile the logged in user is vieweing
    const user_profile = document.querySelector('#user_profile').innerHTML;

    // get csrf token
    const csrftoken = getCookie('csrftoken');

    // fetch
    fetch('/follow_unfollow', {
        method: 'POST',
        headers: { "X-CSRFToken": csrftoken },
        body: JSON.stringify({
            logged_in_user: logged_in_user,
            user_profile: user_profile
        })
    })
    .catch(error => {
        console.log('Error: ', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}