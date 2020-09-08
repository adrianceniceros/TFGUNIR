<?php
	$_SESSION["LAST_ACTIVITY"] = time();
	include_once "includes/clientClass.php";
?>
<h2 class="title-page">Text Classification</h2>
<hr>
</br>
<p>Classify text according to the department who attend the request (Trámites/ Soporte). Introduce the text of the email to try the classifier.</p>

<?php
  $email = "";

  if (($_SERVER["REQUEST_METHOD"] == "POST") && (!empty($_POST["email"]))) {
      $email = test_input($_POST["email"]);
  }

  function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
  }
?>

<form method="post" action="">
	<div class="form-group form-search">
		<textarea name="email" cols="100" rows="10" placeholder="Write down your email here"><?php echo $email?></textarea></br>
		<input type="submit" name="submit" value="Send" class="btn">
	</div>
</form>

 <?php
	if(!empty($email)){
		$auth = $userSession->getCurrentUser() . ":" . $userSession->getCurrentPass();
		
		$emailURL = curl_init("http://82.223.244.47:5000/v1/emailtxt");
		$post_fields = array();
		$post_fields['texto'] = $email;
		$headers = array("Content-Type" => "multipart/form-data");
		
		curl_setopt($emailURL, CURLOPT_USERPWD, $auth);
		curl_setopt($emailURL, CURLOPT_POST,1);
		curl_setopt($emailURL, CURLOPT_POSTFIELDS,$post_fields);
		curl_setopt($emailURL, CURLOPT_HTTPHEADER, $headers);
		curl_setopt($emailURL, CURLOPT_RETURNTRANSFER, 1);
		
		try{
			$jsonData = curl_exec($emailURL);
			if((!curl_errno($emailURL) && curl_getinfo($emailURL, CURLINFO_HTTP_CODE) == 200)){
				$data = json_decode($jsonData, true);
			}
			
			if (!empty($data)){
				echo $data;
			}
			else {echo "</br>La clasificación ha fallado. Inténtalo de nuevo más tarde.";}
		}
		catch (Exception $e) {
			echo 'Caught exception: ',  $e->getMessage(), "\n";
		}
	}			
?>
 
