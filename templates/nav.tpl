<nav class="navbar navbar-expand-lg navbar-light " style="background-color: #e3f2fd;">
    <a class="navbar-brand" href="#">Navbar</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
            <li class="nav-item active">
                <a class="nav-link" href=""{{ url_for('mypage') }}"">My page <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
                <form action="{{ url_for('logout') }}" method="post">
                    <input type="submit" name="logout" value="logout" class="btn btn-outline-success my-2 my-sm-0" />
                </form>
            </li>
        </ul>
    </div>
</nav>
