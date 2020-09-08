<?php
	include_once "html/includes/user_session.php"; 
	$userSession = new UserSession();
	if(($userSession->getCurrentUser()==null) || (($_SERVER['REQUEST_TIME'] - $_SESSION['LAST_ACTIVITY'])>7200)){
	$userSession->closeSession();
		header('Location: login.php');
	} else{
		$username = $userSession->getCurrentUser();
		$password = $userSession->getCurrentPass();
	}
?>

<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="Pagina churn">
		<title>Arsys ML Tools</title>
		<link rel="icon" type="image/x-icon" href="/images/favicon.ico">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
		<link rel="stylesheet" href="css/styles.css" type="text/css">
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
	</head>
	<body>
		<div class="topbar">
			<h1>ARSYS ML TOOLS</h1>
		</div>
		<!-- include "includes/topbar.php" nocache -->
		<!-- < ?php  include_once("includes/topbar.php"); ? >  -->

		<div class="container-fluid"> <!-- container-fluid -->
			<div class="row">
				<div class="col-xs-12 col-md-3 col-lg-2 sidebar">
						<nav>
                                                        <a href="?page=email">Email Classification</a>
                                                        <a href="?page=emailtxt">Text Classification</a>
                                                        <a href="?page=check">Check predictions</a>
                                                        <a href="?page=phishing">Manage Phishing</a>
							<div class="divider"></div>
							<a href="/html/includes/logout.php">Log out</a> 
						</nav>

					<!-- DROPDOWN MENU

						<li class="dropdown">
							<a class="dropdown-toggle" data-toggle="dropdown" href="#">Clients<b class="caret"></b>
							</a>
							<ul class="dropdown-menu">
								<li class="menu-item">Search Client</li>
								<li class="menu-item">Churn List</li>
							</ul>
						</li> -->

					<!-- 
						ORIGINAL
						
						<button class="dropdown-btn"> Clients <i class="fa fa-caret-down"></i></button>
						<div class="dropdown-container">
							<a href="?page=client">Client</a>
							<a href="?page=churn">Churn</a>
						</div>
						<a href="/includes/logout.php">Log out</a> -->
					
					<!-- 
						BOOTSTRAP
						
						<nav class="bd-links" id="bd-docs-nav"> 

							<div class="menu-item">
								<a class="menu-link" href="?page=html/client">
									Clients
								</a>

								<ul class="nav sidenav">
									<li><a href="?page=html/client">Search Client</a></li>
									<li><a href="?page=html/churn">Churn List</a></li>
								</ul>
							</div>

							<div class="menu-item active">
								<a class="menu-link" href="/html/includes/logout.php">Log out</a>
							</div>
						</nav> -->
				</div>

				<main class="col-xs-12 col-md-9 col-lg-8" role="main">
					<div class="content">

						<?php
								if(isset($_GET['page']) && $_GET['page']!=""){
									$page = "";
									switch ($_GET['page']) {
										case 'client':
											$page = "html/client.php";
											break;

										case 'churn':
											$page = "html/churn.php";
											break;
                                                                                case 'email':
                                                                                        $page = "html/email.php";
                                                                                        break;
                                                                                case 'emailtxt':
                                                                                        $page = "html/emailtxt.php";
                                                                                        break;
										case 'phishing':
                                                                                        $page = "html/phishing.php";
                                                                                        break;
                                                                                case 'check':
                                                                                        $page = "html/check.php";
                                                                                        break;


									}

									include_once($page);
							}
						?>
					</div>
				</main>
			</div>


		<script>
			var dropdown = document.getElementsByClassName("dropdown-btn");
			var i;
			for (i = 0; i < dropdown.length; i++) {
				dropdown[i].addEventListener("click", function() {
					this.classList.toggle("active");
					var dropdownContent = this.nextElementSibling;
					if (dropdownContent.style.display === "block") {
						dropdownContent.style.display = "none";
					} else {
						dropdownContent.style.display = "block";
					}
				});
			}
		</script>
	</body>
</html>
