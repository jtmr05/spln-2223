#!/usr/bin/env perl

use v5.36;
use autodie;

use constant PDF_INPUT_PATH  => 'data/medicina.pdf';
use constant XML_INPUT_PATH  => 'data/medicina.xml';
use constant XML_OUTPUT_PATH => 'data/medicina_out.xml';

use constant VAR_MARK => '\/';
use constant SIN_MARK => '$$';
use constant PT_LAN_MARK => '%%PT';
use constant EN_LAN_MARK => '%%EN';
use constant ES_LAN_MARK => '%%ES';
use constant LT_LAN_MARK => '%%LT';


sub main(){
	
	system 'pdftohtml -xml -f 20 -l 544 ' . PDF_INPUT_PATH . ' ' . XML_INPUT_PATH
		unless(-f XML_INPUT_PATH);


	open my $ifh, '<', XML_INPUT_PATH;
	open my $ofh, '>', XML_OUTPUT_PATH;

	while(my $line = <$ifh>){

		if($line =~ m|^<text.+font="(\d+)">(.+?)</text>$| and $1 == 2){
			next;
		}


		if(!defined $2){
			print $ofh $line;
		}
		else {

			my $within_tags = $2;
			$within_tags =~ s/^\s*(.*?)\s*$/$1/gm;

			if($within_tags eq 'pt'){
				print $ofh (PT_LAN_MARK . $line);
			}
			elsif($within_tags eq 'en'){
				print $ofh (EN_LAN_MARK . $line);
			}
			elsif($within_tags eq 'es'){
				print $ofh (ES_LAN_MARK . $line);
			}
			elsif($within_tags eq 'la'){
				print $ofh (LT_LAN_MARK . $line);
			}
			elsif($within_tags =~ m/^VAR\./){
				print $ofh (VAR_MARK . $line);
			}
			elsif($within_tags =~ m/^SIN\./){
				print $ofh (SIN_MARK . $line);
			}
			else {
				print $ofh $line;
			}
		}
	}
}

main();
