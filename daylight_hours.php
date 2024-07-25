<?php

$all = [];
if (($handle = fopen("coordinates.csv", "r")) !== FALSE) {
  while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
      $all[] = $data;
  }
  fclose($handle);
}
array_shift($all);
$daylights = [];
$count = 1;

foreach ($all as $row) {
  $city = $row[0];
  $lat = $row[1];
  $lon = $row[2];
  for ($year = 2012; $year < 2024; $year++) {
    for ($month = 1; $month < 13; $month++) {
      $bound = cal_days_in_month(CAL_GREGORIAN, $month, $year);
      for ($day = 1; $day <= $bound; $day++) {
        $date = "";
        if ($day < 10) {
          $date .= "0";
        }
        $date .= "$day.";
        if ($month < 10) {
          $date .= "0";
        }
        $date .= "$month.$year";
        $info = date_sun_info(strtotime($date), $lat, $lon);
        $diff = $info["sunset"] - $info["sunrise"];
        $daylights[] = [$city, $date, $diff];
      }
    }
  }
  print("$count: $city\n");
  $count++;
}
print(count($daylights));
