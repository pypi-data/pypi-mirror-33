#!/usr/env/bin python3

import click

@click.command()
#@click.option('--outname', prompt='Output file name',
#              help='The name of the output file.')
@click.option('--complete/--no-complete', default=False,help='Input new translations where no merge is available.')
@click.option('--check/--no-check', default=False,help='Check translation that will be merged, or provide new.')
@click.argument('xlffile')#, help='Name of the xlffile to combine with pre-existing translation file.')
@click.argument('mergefile',required=False)#, help='Name of the xlffile to merge into new translation file.')
def merge(xlffile,mergefile,outname=None,complete=False,check=False):
    """Simple program that merges xlffile and mergefile."""
    import xml.etree.ElementTree as ET
    namespaceXLF = {
        'ns0':'urn:oasis:names:tc:xliff:document:1.2'
    }
    click.echo('Merging {} and {}'.format(xlffile, mergefile))
    if mergefile:
        try: availableTranslations = ET.parse(mergefile)
        except ET.ParseError:
            print('Check if xlf file does not start with a google translated comment or other comment and remove')
            raise
        availableTranslations = {
            e.find('ns0:source',namespaceXLF).text: e.find('ns0:target',namespaceXLF).text
            for e in availableTranslations.findall('**/ns0:trans-unit',namespaceXLF)
            if e.find('ns0:target',namespaceXLF) is not None
        }
    else: availableTranslations = {}
    # now that availableTranslations is ready, check where they can be applied
    xlf = ET.parse(xlffile)
    merges = 0
    for e in xlf.findall('**/ns0:trans-unit',namespaceXLF):
        if e.find('ns0:target',namespaceXLF) is None:
            target = ET.Element('ns0:target')
            if e.find('ns0:source',namespaceXLF).text in availableTranslations:
                text = availableTranslations[
                    e.find('ns0:source',namespaceXLF).text
                ]
                if check:
                    click.echo(e.find('ns0:source',namespaceXLF).text)
                    click.echo('Translation: '+text)
                    alttran = input('New translation (leave blank if ok): ')
                    text = alttran if alttran else text
                merges+=1
                target.text = text
                e.append(target)
            elif complete:
                click.echo(e.find('ns0:source',namespaceXLF).text)
                target.text = input('Translation:\n')
                if target.text:
                    e.append(target)
                    merges+=1
    click.echo('{} merges applied'.format(merges))
    with open(outname if outname else xlffile+'_merged','wb') as outfile:
        outfile.write(b'<?xml version="1.0" encoding="UTF-8" ?>\n')
        xlf.write(outfile,encoding='UTF-8')
    
if __name__ == '__main__':
    merge()
