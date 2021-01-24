console.log('script running')

document.addEventListener('DOMContentLoaded', function() {
    const follow_unfollow_btn = document.querySelector('#follow_unfollow_btn');
    if (follow_unfollow_btn === null) {
        console.log('follow_unfollow_btn not found')
    } else {
        follow_unfollow_btn_text();
        follow_unfollow_btn.onclick = follow_unfollow;
    }

    document.querySelectorAll('#edit_post_link').forEach(link => {
        link.addEventListener('click', function() {
            // console.log(this.dataset.postid);
            edit_post(this);
        });
    });


});

// function to edit post
function edit_post(link) {
    const postid = link.dataset.postid
    console.log('edit button clicked for postid ' + postid);

    // find the content row
    const content_row = document.querySelector('#content_row' + postid);
    const original_content_row = content_row.innerHTML;
    
    // find the div of interest
    const content_div = document.querySelector('#post' + postid);

    // save the original post content
    const original_post = content_div.innerHTML;

    // create a text area filled with the original post content
    const textarea = document.createElement('textarea'); 
    textarea.className = 'form-control'; textarea.value = original_post; 
    textarea.maxLength = '280'; textarea.style = 'height: 5em; width: 100%;';

    // empty the content of div
    content_div.innerHTML = '';

    // append the text area to div
    content_div.append(textarea);

    //remove edit link
    const edit_div = document.querySelector('#edit_div' + postid);
    edit_div.innerHTML = '';

    // create save link
    const save_link = document.createElement('a'); save_link.innerHTML = 'Save'; save_link.href = '#';
    edit_div.append(save_link);

    // create cancel link
    const cancel_link = document.createElement('a'); cancel_link.innerHTML = 'Cancel'; 
    cancel_link.href = '#'; cancel_link.style = 'padding-left: 1em;';
    cancel_link.onclick = function() {return false;};
    edit_div.append(cancel_link);

    cancel_link.addEventListener('click', function() {
        console.log('cancel button clicked');
    });
}

//  set the right text for unfollow/follow button
function follow_unfollow_btn_text() {
    console.log('updating follow/unfollow button text')

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

// follow/unfollow in database
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
    .then(response => response.json())
    .then(json => {
        console.log(json)

        // update text when button
        follow_unfollow_btn_text();

        // update followers count
        document.querySelector('#followers_count').innerHTML = json.followers;
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