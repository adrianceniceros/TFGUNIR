<?php
        $_SESSION["LAST_ACTIVITY"] = time();
        include_once "includes/clientClass.php";
?>
<h2 class="title-page">Check Prediction</h2>
<hr>

<?php
  $wrong = "";
  if (($_SERVER["REQUEST_METHOD"] == "POST") && (!empty($_POST['eval']))) {
     $eval = $_POST['eval'];
	 $idppred = $pred[0];

  }

?>
 

<p>Older prediction not checked</p>

<?php
        // first we get the stream context to authorize ourselfs
        $auth = $userSession->getCurrentUser().":".$userSession->getCurrentPass();
        $auth64 = base64_encode($auth);
        $context = stream_context_create([
                "http" => [
                        "header" => "Authorization: Basic $auth64"
                ]
        ]);
        $response = file_get_contents("http://82.223.244.47:5000/v1/check",false, $context);
        $jsonResponse = json_decode($response,true);
        $pred = $jsonResponse["list"];
		
        echo "<p> <b>ID Prediction:</b>".$pred[0]." </br>";
        echo "<b>ID Email:</b> ".$pred[1]." </br></br>";
        echo "<b>Predicted department:</b> ".$pred[2]." </br>";
        echo "<b>% of confidence with the predict:</b> ".$pred[3]." </br></br>";
        echo "<b>Text:</b> ".$pred[4]." </p></br>";
 ?>


<form method="post" action="">
        <div class="form-group form-search">
                <input type="radio" name="eval" value="right"> Mark as right prediction</br>         
                <input type="radio" name="eval" value="wrong"> Mark as wrong prediction<br><br></br>
                <input type="submit" name="submit" value="Send" class="btn">
        </div>
</form>

<?php
       if(!empty($eval)){
                $auth = $userSession->getCurrentUser() . ":" . $userSession->getCurrentPass();
                
                $emailURL = curl_init("http://82.223.244.47:5000/v1/check");
                $post_fields = array();
                $post_fields['eval'] = $eval;
                $post_fields['idpred'] = $pred[0];
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
                                echo $data;
                        }
                        
                }
                catch (Exception $e) {
                        echo 'Caught exception: ',  $e->getMessage(), "\n";
                }
        }                       
?>