<!doctype html>
<html class="no-js" lang="zxx">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>FitNet | Nutritional Needs Calculator</title>
    <meta name="author" content="FitNet Ltd.">
    <meta name="description" content="FitNet is The Most Advanced, Integrated Gamification-Based Application to Keep Fit and Be Healthier.">
    <meta name="keywords" content="workout, app, application, mobile, fit, fitness, nutrition, trainer, coach, trainee, train, training, ">
    <!-- <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> -->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="manifest" href="site.webmanifest">
    <meta name="theme-color" content="#0063CC" />
    <link rel="shortcut icon" type="image/x-icon" href="../assets/img/favicon.png">
    <!-- Main: #0063CC -->
    <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.min.css'>
    <link rel="stylesheet" href="./style.css">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.5.0/css/all.css">
  </head>
  <body>
  <div class="container" style="text-align: center; font-weight: 500; font-size: 23px;">
  <h3 style="text-align: center; font-weight: 500; font-size: 35px;">According to Entered Data, You Need The Following:</h3><hr>
    <?php 
        $age = $_POST['age'];
        $weight = $_POST['weight'];
        $height = $_POST['height'];
        $gender = $_POST['gender'];
        $activity = $_POST['activity'];

        function nBetween($varToCheck, $low, $high) {
        if($varToCheck < $low) return false;
        if($varToCheck >= $high) return false;
        return true;
        }

        switch( $gender ){
            case "male":
                switch( $age ){
                    case "1":
                        switch( $activity ){
                            case "s":
                                echo ("2,400 Calories Per Day,");
                                echo ("<br>");
                                echo ("400 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,800 Calories Per Day,");
                                echo ("<br>");
                                echo ("466 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("3,200 Calories Per Day,");
                                echo ("<br>");
                                echo ("533 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                    case "2":
                        switch( $activity ){
                            case "s":
                                echo ("2,600 Calories Per Day,");
                                echo ("<br>");
                                echo ("433 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,800 Calories Per Day,");
                                echo ("<br>");
                                echo ("466 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("3,000 Calories Per Day,");
                                echo ("<br>");
                                echo ("500 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                    case "3":
                        switch( $activity ){
                            case "s":
                                echo ("2,400 Calories Per Day,");
                                echo ("<br>");
                                echo ("400 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,800 Calories Per Day,");
                                echo ("<br>");
                                echo ("466 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("3,000 Calories Per Day,");
                                echo ("<br>");
                                echo ("500 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                }
            break;

            case "female":
                switch( $age ){
                    case "1":
                        switch( $activity ){
                            case "s":
                                echo ("1,800 Calories Per Day,");
                                echo ("<br>");
                                echo ("300 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,000 Calories Per Day,");
                                echo ("<br>");
                                echo ("333 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("2,400 Calories Per Day,");
                                echo ("<br>");
                                echo ("400 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                    case "2":
                        switch( $activity ){
                            case "s":
                                echo ("2,000 Calories Per Day,");
                                echo ("<br>");
                                echo ("333 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,200 Calories Per Day,");
                                echo ("<br>");
                                echo ("366 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("2,400 Calories Per Day,");
                                echo ("<br>");
                                echo ("400 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                    case "3":
                        switch( $activity ){
                            case "s":
                                echo ("2,000 Calories Per Day,");
                                echo ("<br>");
                                echo ("333 Grams of Carbs Per Day,");
                            break;
                            case "ma":
                                echo ("2,200 Calories Per Day,");
                                echo ("<br>");
                                echo ("366 Grams of Carbs Per Day,");
                            break;
                            case "a":
                                echo ("2,400 Calories Per Day,");
                                echo ("<br>");
                                echo ("400 Grams of Carbs Per Day,");
                            break;
                        }
                    break;
                }
            break;
        }

        echo ('<br>');

        if (nBetween($weight, 50, 60)) {
            echo ("44 Grams of Proteins Per Day.");
        }
        elseif (nBetween($weight, 60, 70)) {
            echo ("52 Grams of Proteins Per Day.");
        }
        elseif (nBetween($weight, 70, 80)) {
            echo ("60 Grams of Proteins Per Day.");
        }
        elseif (nBetween($weight, 80, 90)) {
            echo ("68 Grams of Proteins Per Day.");
        }
        elseif (nBetween($weight, 90, 101)) {
            echo ("76 Grams of Proteins Per Day.");
        }
    ?>
    <hr>
    <a href="./" style="color: #000; font-size:45px; display: inline-block; line-height: normal; margin-right: 15px; margin-left: 15px;"><style>a{text-decoration:none;} a:hover i{color: #0063CC;}</style><i class="fas fa-arrow-left"></i></a>
    <a href="../" style="color: #000; font-size:45px; line-height: normal; margin-right: 15px; margin-left: 15px;"><style>a{text-decoration:none;} a:hover i{color: #0063CC;}</style><i class="fa fa-home" aria-hidden="true"></i></a>
  </div>
  </body>
</html>