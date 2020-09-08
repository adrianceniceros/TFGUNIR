<?php
class UserSession{
    public function __construct(){
        session_start();
    }
    public function setCurrentUser($user,$pass){
				$_SESSION['user'] = $user;
				$_SESSION['pass'] = $pass;
				$_SESSION['LAST_ACTIVITY'] = $_SERVER['REQUEST_TIME'];
    }
    public function getCurrentUser(){
        return $_SESSION['user'];
    }
    public function getCurrentPass(){
        return $_SESSION['pass'];
    }
    public function closeSession(){
        session_unset();
        session_destroy();
    }
}
?>
