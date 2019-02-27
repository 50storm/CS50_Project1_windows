<nav class="navbar navbar-expand-lg navbar-light " style="background-color: #e3f2fd;">
    <a class="navbar-brand" href="#">Navbar</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
            <li id="mypage" class="nav-item">
                <a class="nav-link" href="{{ url_for('mypage') }}">My Page</a>
            </li>
            <li id="myaccount" class="nav-item ">
                <a class="nav-link"  href="{{ url_for('showUserAccount') }}">My User Account</a>
            </li>
            <li id="search" class="nav-item ">
                <a class="nav-link" href="{{ url_for('search') }}">Search Books</a>
            </li>
            <li class="nav-item">
                <form action="{{ url_for('logout') }}" method="post">
                    <!-- <input type="submit" name="logout" value="logout" class="btn btn-outline-info my-2 my-sm-0" /> -->
                    <input type="submit" name="logout" value="Logout" class="btn my-2 my-sm-0 bg-primary-light"  style="background-color: #e3f2fd;" />
                </form>
            </li>
        </ul>
    </div>
</nav>
