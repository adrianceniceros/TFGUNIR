<?php
class User{

	private $name;

	public function userExists($user, $pass){
		// first we create and execute the curl with the credentials
		$curl = curl_init('http://82.223.244.47:5000/v1/ping');
		curl_setopt($curl, CURLOPT_USERPWD,$user . ":" . $pass);
   	curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
		curl_exec($curl);

		//return true if the authentication was correct
		if(!curl_errno($curl) && curl_getinfo($curl, CURLINFO_HTTP_CODE) == 200){
			return true;
		}

		return false;
	}

	public function getNombre(){
		return $this->name;
	}

}
?>
