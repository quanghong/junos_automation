use Net::Netconf::Manager;
        print "Enter hostname\n";
        my $hostname = <>;

        print "Enter username\n";
        my $login= <>;

        print "Enter password\n";
        my $pass = <>;
        chomp($hostname);
        chomp($login);
        chomp($pass);
        $jnx = new Net::Netconf::Manager( 'access' => 'ssh',
                      'login' => $login,
                      'password' => $pass,
                      'hostname' => $hostname);
        if(! $jnx ) {
              print STDERR "Unable to connect to Junos device \n";
              exit 1;
         }
         print "Connection established: " . $jnx->get_session_id . "\n";
         my $reply=$jnx->get_system_information();
         if ($jnx->has_error) {
         print "ERROR: in processing request\n";
         # Get the error
         my $error = $jnx->get_first_error();
         $jnx->print_error_info(%$error);
         exit 1;
         }
 	  print "Server request: \n $jnx->{'request'}\n Server response: \n $jnx->{'server_response'} \n";

         # this parsing is specifically for <get-system-information> tag
         # you can write your own application in similar way
         #parsing reply from server
         my $config= $jnx->get_dom();
         $res= $config->getElementsByTagName("hardware-model")->item(0)->getFirstChild->getData;
         $res2= $config->getElementsByTagName("os-name")->item(0)->getFirstChild->getData;
         $res3= $config->getElementsByTagName("host-name")->item(0)->getFirstChild->getData;
         print "\nhardware information  ". $res ."\n";
         print "os-name  " .$res2 . "\n";
         print "host-name  ". $res3. "\n";
         $jnx->disconnect();
