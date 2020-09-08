<?php
	$_SESSION["LAST_ACTIVITY"] = time();
	include_once "includes/clientClass.php";
?>
<h2 class="title-page">Email Classification</h2>
<hr>
</br>
<p>Classify emails according to the department that should attend the request (Trámites/ Soporte). Also return if the email content phishing URLs. </br>Introduce the text of the email to try the classifier.</p>

<?php
   $email = "";
   
   if(($_SERVER["REQUEST_METHOD"] == "POST") && (!empty($_FILES["file"]))){
      $errors= array();
      $file_name = $_FILES['file']['name'];
      $file_size =$_FILES['file']['size'];
      $file_tmp =$_FILES['file']['tmp_name'];
      $file_type=$_FILES['file']['type'];
      $file_ext=strtolower(end(explode('.',$_FILES['file']['name'])));
      
      $extensions= array("txt", "eml");
      
      if(in_array($file_ext,$extensions)=== false){
         $errors[]="extension not allowed.";
      }
      
      if($file_size > 2097152){
         $errors[]='File size must be excately 2 MB';
      }
      
      if(empty($errors)==true){
         move_uploaded_file($file_tmp,"/var/www/worktogethernow/emails/".$file_name);
         $_file = fopen("/var/www/worktogethernow/emails/".$file_name, 'r');
		 $email = fread($_file, $file_size);
		 fclose($_file);
		 unlink("/var/www/worktogethernow/emails/".$file_name);
      }else{
         print_r($errors);
      }
   }
?>

<form method="post" action="" enctype="multipart/form-data">
	<div class="form-group form-search">
        <input type="file" name="file">
        </br></br>
        <input type="submit" name="submit" value="Send" class="btn">
	</div>
</form>
<hr>

 <?php
        if(!empty($email)){
                $auth = $userSession->getCurrentUser() . ":" . $userSession->getCurrentPass();
                
                $emailURL = curl_init("http://82.223.244.47:5000/v1/email");
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
							echo '<b>HTTP CODE:</b> <span style="color:green">OK</span></br>';
                        }
						else {
							echo '<b>HTTP CODE:</b> <span style="color:red">KO</span></br>';
						}
                        if (!empty($data)){
                                $data =  $data['analyzed_mail'];
                                                                $from = $data['_from'];
                                                                $from2 = $from[0][1];
                                                                echo '</br><b>From: </b>' . $from2 . '</br></br>';
                                                                $to = $data['_to'];
                                                                $to2 = $to[0][1];
                                                                echo '<b>To: </b>' . $to2 . '</br></br>';
                                                                echo '<b>Subject:</b> ' . $data['_subject'] . '</br></br>';
								echo '<b>Mail:</b></br>' . $data['_mainText'] . '</br></br></br>';
								echo '<b>Department:</b> ' . $data['_predDpto'] . '</br>';
                                                                echo '<b>% confidence department:</b> ' . $data['_predProb'] . '</br>';
								if ($data['_isPhishing'] == 1){
									echo '<b>Phishing:</b> <span style="color:red">YES</span> </br>';
								}
								else {
									echo '<b>Phishing:</b> <span style="color:green">NO</span> </br>';
								}
                                                                $tokens = $data['_tokens'];
                                                                echo '</br><b>Tokens:</b></br>';
                                                                foreach ($tokens as &$token){
                                                                        echo ' ' . $token . '</br> ';
                                                                }
                                                                
                        }
                        else {echo "</br>La clasificación ha fallado. Inténtalo de nuevo más tarde.";}
                }
                catch (Exception $e) {
                        echo 'Caught exception: ',  $e->getMessage(), "\n";
                }
        }                       
?>
 
