#!/usr/bin/perl -w
 
use strict;
use warnings;


my $numarg = $#ARGV + 1;
if ($numarg < 2) {
    print "Usage: str_replace Search Replace File\nOr: STDIN str_replace Search Replace";
    exit;
}

my $find=$ARGV[0];
my $replace=$ARGV[1];
my $file;
my $contents;
my $found=0;
my $fh;

if(defined $ARGV[2]){
	$file=$ARGV[2];
	open($fh, '<', $file) or die "Cannot open the file '$file'";
		{
			local $/;
			$contents = <$fh>;
		}
	close($fh);
}
else{
	{
		local $/;
		$contents = <STDIN>;
	}
}
my $pos = index($contents, $find);
while ( $pos > -1 ) {
	if(substr( $contents, $pos, length( $find ), $replace )){$found =$found+1;}
	$pos = index( $contents, $find, $pos + length( $replace ));
}

if(!defined $ARGV[2]){
	print $contents;
	exit;
}

if($found==0) {print "Nothing replaced\n";}
else{ print "$found occurrences of '$find' have been replaced with '$replace'\n";}


open($fh, '>', $file);
print $fh $contents;
close $fh;
