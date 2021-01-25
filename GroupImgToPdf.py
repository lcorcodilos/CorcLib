from pylatex import Document, Figure, NoEscape, MiniPage

def GroupImgToPdf(plot_files,outname,margin="0.5in"):
    # Write some LaTeX
    tex = Document(geometry_options={"margin":margin})
    for iplot in range(0,len(plot_files),2):
        plot_left = plot_files[iplot]
        if iplot+1 < len(plot_files):
            plot_right = plot_files[iplot+1]
        else:
            plot_right = False

        with tex.create(Figure(position='h!')) as fig:
            fig.add_image(plot_left,width=NoEscape(r'0.45\textwidth'))
            if plot_right != False: fig.add_image(plot_right,width=NoEscape(r'0.45\textwidth'))

    tex.generate_pdf(outname,clean_tex=False)

if __name__ == "__main__":
    from argparse import ArgumentParser
    import glob
    parser = ArgumentParser()

    parser.add_option('-o', '', metavar='F', action='store', type=str,
                    default   =   '',
                    required  =   True,
                    dest      =   'output',
                    help      =   'Output pdf name')

    parser.add_option('-m', '', metavar='F', action='store', type=str,
                    default   =   '0.5in',
                    dest      =   'margin',
                    help      =   'Margin (with units)')

    (options, args) = parser.parse_args()

    plots = []
    for f in args:
        if '*' in f:
            plots.extend(glob.glob(f))
        else:
            plots.append(f)

    GroupImgToPdf(plots,options.output,margin=options.margin)