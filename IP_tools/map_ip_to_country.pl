#!/usr/bin/env perl

use strict;
use warnings;
use Geo::IP;
use Getopt::Long;
use Text::Table;
use File::Slurp qw(read_file);
use Data::Validate::IP qw(is_public_ipv4);

# map_ip_to_country
# Script for reading in a file and mapping the IP's to their corresponding countries.
# Written to support IPv4.
#
# Author: Erik Lamers <mail@eriklamers.nl>

my $file_location = "";
my $ips = "";
my $verbose = 0;
my $no_validation = 0;
my $remove_faulty = 0;
my @ip_values;
my @validated_ips;

usage() unless GetOptions(
    "h|help"            => \&usage,
    "f|file-location=s" => \$file_location,
    "i|ips=s"           => \$ips,
    "n|no-validation"   => \$no_validation,
    "r|remove-faulty"   => \$remove_faulty,
    "v|verbose"         => \$verbose,
);

initial_checks();
print "Argument checks successful\n" if $verbose;
if ($file_location) {
    @ip_values = get_values_from_file();
} else {
    @ip_values = split(/ /, $ips);
}

unless ($no_validation) {
    print "Validating IP's\n" if $verbose;
    @validated_ips = validate_ips(@ip_values);
    print "IP validation successful\n" if $verbose;
} else {
    @validated_ips = @ip_values;
}
undef @ip_values;

print "Mapping IP's to corresponding countries\n" if $verbose;
my $results = map_ips_to_country(@validated_ips);

print "\n".$results."\n";

sub get_values_from_file {
    my @lines = read_file($file_location);
    chomp @lines;
    return @lines;
}

sub initial_checks {
    if (! $file_location && ! $ips) {
        usage("Either --file-location or --ips must be given!");
    }
    if ($file_location && $ips) {
        usage("--file-location and --ips are mutually exclusive, they cannot be passed at the same time!");
    }

    if ($no_validation && $remove_faulty) {
        usage("--no-validation and --remove-faulty cannot be passed at the same time!");
    }

    if ($file_location && ! -f $file_location) {
        die("$file_location is not a valid file!");
    }
}

sub validate_ips {
    my @ips_to_validate = @_;
    my $iterator = 0;

    foreach my $ip (@ips_to_validate) {
        print "Validating $ip\n" if $verbose;
        if (! is_public_ipv4($ip)) {
            if ($remove_faulty) {
                print "Removing bogus entry from list: $ip\n" if $verbose;
                splice(@ips_to_validate, $iterator, 1);
            } else {
                die("$ip is not a valid IP!");
            }
        }
        $iterator++;
    }
    return @ips_to_validate
}

sub map_ips_to_country {
    my @ips_to_map = @_;
    my $table = Text::Table->new("IP", \" | ", "CC");
    my $gi = Geo::IP->new(GEOIP_MEMORY_CACHE);
    foreach my $ip (@ips_to_map) {
        my $country = $gi->country_code_by_addr("$ip");
        $table->add($ip, $country);
    }
    return $table;
}

sub usage {
    my $msg = shift || '';
    print<< "       END";
    $0 Tool for quickly mapping IP's to their corresponding countries

    Usage:
    $0 -i <ip> -f <file> [-v] [-n]

    Examples:
    $0 -f /tmp/ips
    $0 -i "8.8.8.8 1.1.1.1"

    Args:
    -f, --file-location     - Load IP's from a file instead of the command line
    -i, --ips               - IP's to process (separated by spaces)
    -n, --no-validation     - Do not validate the IP's
    -r, --remove-faulty     - Ignore IP's that do not pass IP validation
    -v, --verbose           - Be more verbose

       END
    print "$msg\n" if $msg;
    exit 1;
}
