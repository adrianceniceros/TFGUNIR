<?php
        $_SESSION["LAST_ACTIVITY"] = time();
        include_once "includes/clientClass.php";
?>
<h2 class="title-page">Phishing Management</h2>
<hr>
</br>
<p>Insert the URL considered phishing</p>

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
                <textarea name="email" cols="100" rows="1" placeholder="Write down your URL here"><?php echo $email?></textarea></br>
                </br>
                <input type="submit" name="submit" value="Send" class="btn">
        </div>
</form>



 <?php
        if(!empty($email)){
                $auth = $userSession->getCurrentUser() . ":" . $userSession->getCurrentPass();
                
                $emailURL = curl_init("http://82.223.244.47:5000/v1/phishing");
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
                        else {echo "</br>Error detected. Try again later.";}
                }
                catch (Exception $e) {
                        echo 'Caught exception: ',  $e->getMessage(), "\n";
                }
        }                       
?>
 

</br>
</br>
<h2 class="title-page">URLs classified as phishing in the last 60 days</h2>
<table>
        <?php
                // first we get the stream context to authorize ourselfs
                $auth = $userSession->getCurrentUser().":".$userSession->getCurrentPass();
                $auth64 = base64_encode($auth);
                $context = stream_context_create([
                        "http" => [
                                "header" => "Authorization: Basic $auth64"
                        ]
                ]);
                $response = file_get_contents("http://82.223.244.47:5000/v1/phishing",false, $context);
                $jsonResponse = json_decode($response,true);
                $List = $jsonResponse["list"];

                echo "<tr><th>URL</th><th>Date added</th> </tr>";
                foreach($List as $itemRow){
                    echo "<tr>\n";
                    $valor = $itemRow[0];
                    $valor2 = $itemRow[1];
                    echo "\t <td> $valor  </td>\n";
                    echo "\t <td>$valor2</td>\n";
                    echo "</tr>\n";
                }

        ?>
</table>
