#!/usr/bin/perl
use strict;
use warnings;

my %counts;
my %lines;
my @headers;

while (<>) {
    chomp;
    if (/^\@/) {
        push @headers, $_;
        next;
    }
    # -1 保留所有字段, 包括结尾的空字段
    my @fields = split(/\t/, $_, -1);
    my $qqname = $fields[0];
    $counts{$qqname}++;
    push @{$lines{$qqname}}, $_;
}

# 输出头部信息
print join("\n", @headers), "\n" if @headers;

# 输出成对 read
foreach my $qname (keys %counts) {
    if ($counts{$qname} == 2) {
        print join("\n", @{$lines{$qname}}), "\n";
    }
}
