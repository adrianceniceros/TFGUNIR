<?php

class NotFoundException extends Exception{}

class Client{

	const ID_MSG = "ID";
	const TENURE_MSG = "Tenure (days)";
	const MEANCONTRACTLENGTH_MSG = "Mean Contract Length (days)";
	const ACTIVEFREESERVICES_MSG = "Active free services";
	const ACTIVEPAYMENTSERVICES_MSG = "Active payment services";
	const SERVICESDOWN_MSG = "Services down (last 6 months)";
	const ANNUALTURNOVER_MSG = "Annual turnover (€)";
	const BILLPROBLEM6M_MSG = "Bill problems (last 6 months)";
	const BILLPROBLEM3M_MSG = "Bill problems (last 3 months)";
	const CHURN_MSG = "Churn";
	const SCORE_MSG = "Score";
	const NPS_MSG = "NPS";

	private $ID;
	private $tenure;
	private $meanContractLength;
	private $activeFreeServices;
	private $activePaymentServices;
	private $servicesDown;
	private $annualTurnover;
	private $billProblem6M;
	private $billProblem3M;
	private $churn;
	private $score;
	private $NPS;

	public function __construct($ID, $auth){
		$dataURL = curl_init("http://82.223.244.47:5000/v1/customers/$ID");
		$scoreURL = curl_init("http://82.223.244.47:5000/v1/customers/churn/$ID");
 		curl_setopt($dataURL, CURLOPT_USERPWD, $auth);
		curl_setopt($scoreURL, CURLOPT_USERPWD,$auth);
		curl_setopt($dataURL, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($scoreURL, CURLOPT_RETURNTRANSFER, 1);
		$jsonData = curl_exec($dataURL);
		$jsonScore = curl_exec($scoreURL);

		if((!curl_errno($dataURL) && curl_getinfo($dataURL, CURLINFO_HTTP_CODE) == 200) && (!curl_errno($scoreURL) && curl_getinfo($scoreURL, CURLINFO_HTTP_CODE) == 200)){
			$data = json_decode($jsonData, true);
			$score = json_decode($jsonScore, true);
			$this->ID = $ID;
			$this->tenure = $data['antiguedad'];
			$this->meanContractLength = $data['tMedioContr'];
			$this->activeFreeServices = $data['servActGrat'];
			$this->activePaymentServices = $data['servActPago'];
			$this->servicesDown = $data['servBajaUlt6Meses'];
			$this->annualTurnover = $data['factAnual'];
			$this->billProblem6M = $data['incFactUlt6Meses'];
			$this->billProblem3M = $data['incFactUlt3Meses'];
			$this->NPS = $data['NPS'];
			$this->churn = $score['churn'];
			$this->score = $score['score'];
		} else{
			throw new NotFoundException();
    }
	}

	public static function load($ID, $auth) {
		try{
			return new Client($ID, $auth);
		} catch (NotFoundException $e){
			return NULL;
		}
	}

	public function getID(){
		return $this->ID;
	}

	public function getTenure(){
		return $this->tenure;
	}

	public function getMeanContractLength(){
		return $this->meanContractLength;
	}

	public function getActiveFreeServices(){
		return $this->activeFreeServices;
	}

	public function getActivePaymentServices(){
		return $this->activePaymentServices;
	}

	public function getServicesDown(){
		return $this->servicesDown;
	}

	public function getAnnualTurnover(){
		return $this->annualTurnover;
	}

	public function getBillProblem6M(){
		return $this->billProblem6M;
	}

	public function getBillProblem3M(){
		return $this->billProblem3M;
	}

	public function getChurn(){
		return $this->churn;
	}

	public function getScore(){
		return $this->score;
	}

	public function getNPS(){
		return $this->NPS;
	}

	public static function attString($att){
		switch($att){
			case 'ID':
				$msg = self::ID_MSG;
				break;
			case 'tenure':
				$msg = self::TENURE_MSG;
				break;
			case 'meanContractLength':
				$msg = self::MEANCONTRACTLENGTH_MSG;
				break;
			case 'activeFreeServices':
				$msg = self::ACTIVEFREESERVICES_MSG;
				break;
			case 'activePaymentServices':
				$msg = self::ACTIVEPAYMENTSERVICES_MSG;
				break;
			case 'servicesDown':
				$msg = self::SERVICESDOWN_MSG;
				break;
			case 'annualTurnover':
				$msg = self::ANNUALTURNOVER_MSG;
				break;
			case 'billProblem6M':
				$msg = self::BILLPROBLEM6M_MSG;
				break;
			case 'billProblem3M':
				$msg = self::BILLPROBLEM3M_MSG;
				break;
			case 'churn':
				$msg = self::CHURN_MSG;
				break;
			case 'score':
				$msg = self::SCORE_MSG;
				break;
			case 'NPS':
				$msg = self::NPS_MSG;
				break;
		}
		return $msg;
	}

	public function printClient(){

		//The alert is shown if necessary
		if($this->churn == 0){
			if($this->score >=75){
				echo "<div class='alert'> \n";
				echo "\t <span class='closebtn' onclick=\"this.parentElement.style.display='none';\">&times;</span> \n";
				echo "\t <strong>Danger!</strong> This client has a lot of chances of leaving soon.\n";
				echo "</div> \n";
			} else{
				echo "<div class='warning'> \n";
				echo "\t <span class='closebtn' onclick='this.parentElement.style.display=none;'>&times;</span> \n";
				echo "\t <strong>Warning!</strong> This client has some chances of leaving this year.\n";
				echo "</div> \n";
			}
		}

		//Print the image
		echo "<div class='profile'> \n";
		echo "\t <div class='image'>  \n";
		echo "\t \t <img src='https://adamtheautomator.com/content/images/2019/10/user-1633249_1280.png' width = 200 height = 200 alt = 'Client'> \n";
		echo "\t </div>";
		echo "\t <div class='clientID'>ID: $this->ID </div>  \n";
		echo "</div>";

		//Print the data
		echo "<div class='row'>";
		foreach ($this as $key => $value){
			if($key != 'ID'){
				$msg = self::attString($key);
				echo "<div class='col-xs-12 col-sm-3 col-md-4 col-lg-5 card'> \n";
				if($value!==NULL){
					echo "\t <span class='value'>" . round($value,2) . "</span> \n";
				} else{
					echo "\t <span class='value'> - </span> \n";
				}
				echo "\t <span class='parameter'>$msg</span> \n";
				echo "</div> \n";
			}
		}
		echo "</div>";
		/*
		echo "<div class='stats'>";
		foreach ($this as $key => $value){
			if($key != 'ID'){
				$msg = self::attString($key);
				echo "<div class='box'> \n";
				if($value!==NULL){
					echo "\t <span class='value'>" . round($value,2) . "</span> \n";
				} else{
					echo "\t <span class='value'> - </span> \n";
				}
				echo "\t <span class='parameter'>$msg</span> \n";
				echo "</div> \n";
			}
		}
		echo "</div>";
		*/
	}

	public function printClientRow($header=False){
		if($header){
			echo "<tr>\n";
				foreach($this as $key => $value){
					$head = self::attString($key);
					echo "\t <th> $head  </th>\n";
				}
			echo "</tr>\n";
		}
		echo "<tr> \n";
		foreach ($this as $key => $value){
			if($value!==NULL){
				echo "\t<td> " . round($value,2) . "</td>";
			} else{
				echo "\t<td> -  </td>";
			}
		}
		echo "</tr> \n";
	}

}
?>
