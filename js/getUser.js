window.onload = async function() {
    let response = await fetch('/getUser', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
        const result = await response.json();
        if (result.username) {
            // Display the logged-in dropdown if username is found
            document.getElementById('nav-user-dropdown').innerHTML = `
                <li class="nav-item dropdown">
                        <a class="nav-login-icon nav-link nav-login dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><span style="text-transform: none; vertical-align: top;">WELCOME, ${result.username} </span><img src="/images/login.png" class="navbar-img navbar-img-nohover" height="30px"><img src="/images/loginhover.png" class="navbar-img navbar-img-hover" height="30px"></a>
                        <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                            <a class="dropdown-item" href="/profile">Profile</a>
                            <a class="dropdown-item" href="/bookmarkspage">Bookmarks</a>
                            <a class="dropdown-item" href="/comments">Comments</a>
							<a class="dropdown-item" href="/logout">Log Out</a>
                        </div>
                </li>
            `;
        } else {
            // Display the login/register dropdown if username is not found
            document.getElementById('nav-user-dropdown').innerHTML = `
                <li class="nav-item dropdown">
                        <a class="nav-login-icon nav-link nav-login dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><img src="/images/login.png" class="navbar-img navbar-img-nohover" height="30px"><img src="/images/loginhover.png" class="navbar-img navbar-img-hover" height="30px"></a>
                        <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                            <a class="dropdown-item" href="/login">Log In</a>
                            <a class="dropdown-item" href="/register">Register</a>
                            <a class="dropdown-item" href="/bookmarkspage">Bookmarks</a>
                            <a class="dropdown-item" href="/comments">Comments</a>
                        </div>
                </li>
            `;
        }
    } else {
        // Handle non-200 responses with a fallback
        document.getElementById('nav-user-dropdown').innerHTML = `
            <li class="nav-item dropdown">
                        <a class="nav-login-icon nav-link nav-login dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><img src="/images/login.png" class="navbar-img navbar-img-nohover" height="30px"><img src="/images/loginhover.png" class="navbar-img navbar-img-hover" height="30px"></a>
                        <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                            <a class="dropdown-item" href="/login">Log In</a>
                            <a class="dropdown-item" href="/register">Register</a>
                            <a class="dropdown-item" href="/bookmarkspage">Bookmarks</a>
                            <a class="dropdown-item" href="/comments">Comments</a>
                        </div>
            </li>
        `;
    }
};