#!/usr/bin/env perl

use v5.36;
use utf8;
use autodie;

use constant FILENAME => 'Harry_Potter_e_A_Pedra_Filosofal.txt';

sub get_file_as_str(){

    local $/ = undef;

    open my $ifh, '<:utf8', FILENAME;

    return <$ifh>;
}

my $text = get_file_as_str();
my @poems = ();

sub save_poem($poem){
    push @poems, $poem;
    return "__${\scalar @poems}__\n";
}


#7. Eliminar "==============================================="
$text =~ s/^=*\n.+\n=*$//mg;

#2. Marcar capítulos
$text =~ s/^.*(CAP[IÍ]TULO \w+).*\n(.+?)$/\n# $1 --- $2/mg;

#0. Quebra de página
$text =~ s/([a-z,;-])\n\n([a-z0-9])/$1\n$2/g;

#1. Separar pontuação das palavras
$text =~ s/(\w)(\.\.\.|[.,?!;\–])+/$1 $2/g;
$text =~ s/(Sra|Sr|Profa) \./$1./g;


#3. Separar parágrafos de linhas pequenas
$text =~ s/([a-z0-9,:])\n\n([a-z0-9])/$1\n$2/g;

#5. Uma frase por linha
$text =~ s/(\.|!|\?)\s/$1\n/g;

#4. Juntar linhas da mesma frase
$text =~ s/([^!?.])\n/$1 /g;
$text =~ s/(\.\.\.|–)\n(\w)/$1 $2/g;
$text =~ s/((Sr|Sra|Profa)\.)\n/$1 /g;

#6. Guardar poemas
$text =~ s|<poema>(.*?)</poema>|save_poem($1)|egs;

# Eliminar newline do primeiro capítulo
$text =~ s/^\n//;


binmode STDOUT, ':utf8';
print $text;
