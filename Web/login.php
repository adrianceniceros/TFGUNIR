<?php
	include_once 'html/includes/user.php';
	include_once 'html/includes/user_session.php';

	$userSession = new UserSession();

	if($userSession->getCurrentUser()!= null){
		header('Location: /');
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
		<?php
			$user = new User();
			$username = $password = "";

			if ($_SERVER["REQUEST_METHOD"] == "POST") {
				if (!empty($_POST["Username"])) {
					$username = test_input($_POST["Username"]);
				}
				if (!empty($_POST["Password"])) {
					$password = test_input($_POST["Password"]);
				}
			}

			function test_input($data) {
				$data = trim($data);
				$data = stripslashes($data);
				$data = htmlspecialchars($data);
				return $data;
			}
		?>

		<div class="topbar">
			<h1>ARSYS ML TOOLS</h1>
		</div>

		<div class="content login">
			<h2>Login</h2>

			<form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">
				<div class="form-group">
					<label for="Username">User</label>
					<input type="text" name="Username" id="Username" value="<?php echo $username;?>">
				</div>

				<div class="form-group">
					<label for="Password">Password</label>
					<input type="password" name="Password" id="Password" value="<?php echo $password;?>">
				</div>
				
				<div class="text-center">
					<input type="submit" name="submit" value="Submit" class="btn">
				</div>

			</form>

			<?php
				if(!empty($username) && !empty($password)){
					if($user->userExists($username, $password)){
						$userSession->setCurrentUser($username,$password);
						header('Location: /');
					}else{
						echo '<div class="error">Nombre de usuario y/o password incorrecto.</div>';
					}
				}
			?>
		</div>
	</body>
</html>
