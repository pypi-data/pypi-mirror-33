options(stringsAsFactors = FALSE)
source("http://www.bioconductor.org/biocLite.R")
.libPaths(R_LIB_PATHS)
#biocLite(c("d3heatmap"))
#biocLite(c("heatmaply"))
#biocLite(c("DESeq2"))

# Parallelization
library(BiocParallel)

# Graphics
library(RColorBrewer)
library(gplots)
library(ggplot2)
library(ggdendro)
library(grid)
library(gridExtra)
library(RColorBrewer)

# Analysis
library(DESeq2)
library(matrixStats)
library(amap)
library(magrittr)
library(dplyr) # dplyr after biomaRt!!!!!
library(reshape2)
library(stringr)
library(fdrtool)
library(sva) # for combat function

# html widgets
library(d3heatmap)
library(DT)
library(plotly)
library(heatmaply)
library(S4Vectors)
library(png)

#-------------------------------------------------------------------------------

get_frac_top_genes <- function(countsTable,frac.thresh=0.05){
# Returns the genes with the most counts (and genes above frac.thresh), and the fraction of reads they hold.

  get_top = function(counts.column,frac.thresh){
    sum.counts = sum(counts.column)
    top = c(
      names(which(counts.column/sum.counts>frac.thresh)),
      names(sort(counts.column,decreasing = T)[1:2])
    )
    return(top)
  }

  top.genes = lapply(colnames(countsTable), function(x) get_top(countsTable[,x],frac.thresh=frac.thresh)) %>%
    unlist %>%
    unique

  col_sums = colSums(countsTable)
  frac.top = do.call(rbind,lapply(top.genes,function(gene) countsTable[gene,]/col_sums))
  row.names(frac.top) = top.genes

  return(frac.top)
}



#-------------------------------------------------------------------------------
dds_to_heatmap = function(plot_counts){
  
  dist = plot_counts %>%
    t() %>%
    Dist(.,method='pearson') %>%
    as.matrix(.)
  
  return(1-dist)
  
}


dds_to_distances = function(plot_counts){
  # Calculate distances between samples.
  # plot_counts - DESEq2 object after rld or ComBat (in batch)

  distances = plot_counts %>%
    t() %>%
    Dist(.,method='pearson')

  return(distances)
}

distances_to_dendogram = function(distances, dds){
  # Cluster the dds data, and return a dedogram object that ggplot_dendogram can work with
  # plot_counts - DESEq2 object after rld or ComBat (in batch)

  dendro = distances %>%
    hclust(method = "ward.D") %>%
    dendro_data()

  # Add the coolData info to the labels of the dendro_data object
  dendro$labels = colData(dds) %>%
    as.data.frame() %>%
    tibble::rownames_to_column(var = 'label') %>%
    inner_join(dendro$labels,by = 'label')

  return(dendro)
}


ggplot_dendogram <- function(dendro,factor_for_color){
  # Return a ggplot object with a dendogram of samples clustered by genes
  # factor_for_color - one of the column descriptors from colData(dds) that will be used to color the labels of dendogram

  # Based on: http://stackoverflow.com/questions/11967880/creating-a-legend-for-a-dendrogram-with-coloured-leaves-in-r

  if (is.null(factor_for_color)){
    factor_for_color = names(label(dendro))[2]
  }

  lab = label(dendro)
  colourCount = length(lab[[factor_for_color]])
  getPalette = colorRampPalette(brewer.pal(9, "Set1"))

  gd = ggplot() +
    geom_segment(data=segment(dendro), aes(x=x, y=y, xend=xend, yend=yend)) +
    geom_text(data = label(dendro), aes_string(x='x', y='y', label='label', color = factor_for_color, hjust=0), size=3) +
    coord_flip() +
    scale_y_reverse(expand=c(1.5, 0)) +
    scale_colour_manual(values = getPalette(colourCount)) +
    theme_dendro()

  return(gd)

}


#-------------------------------------------------------------------------

extract_results_for_one_comp = function(dds,Factor,A,B, thresholds){
  if (Factor!="Interaction"){
    res = results(dds, contrast = c(Factor,A,B) , cooksCutoff=FALSE, independentFiltering=FALSE)
  }else{
    dds_output_variables = mcols(mcols(dds),use.names = T)
    which_interaction = grepl("log2 fold change",dds_output_variables[,2]) & !grepl("_vs_|Intercept",row.names(dds_output_variables))
    interaction_name = row.names(dds_output_variables)[which_interaction]
    res = results(dds, cooksCutoff=FALSE, independentFiltering=FALSE, name=interaction_name)
  }

  res.na.pvalue <- res[is.na(res$pvalue),] #mean(res$pvalue > 0.9) > 0.1) throw exception if res$pvalue is na. If cooksCutoff=TRUE there are values with NA
  res <- res[!is.na(res$pvalue),]
  padj_corrected = FALSE
  res_bak <- cbind(res)#deep copy of res

  q1 = res$pvalue <= 0.25 #TRUE/FALSE vector
  q234 = res[res$pvalue > 0.25,]
  t1ofq234 = q234$pvalue > 0.25 & q234$pvalue <= 0.5 #TRUE/FALSE vector
  t2ofq234 = q234$pvalue > 0.5 & q234$pvalue <= 0.75 #TRUE/FALSE vector
  t3ofq234 = q234$pvalue > 0.75 & q234$pvalue <= 1 #TRUE/FALSE vector

  # if (mean(res$pvalue > 0.9) > 0.1) {
  if(mean(q1) < 0.2 || mean(t1ofq234) > 0.38 || mean(t1ofq234) < 0.28 || mean(t2ofq234) > 0.38 || mean(t2ofq234) < 0.28 || mean(t3ofq234) > 0.38 || mean(t3ofq234) < 0.28) {
    padj_corrected<-tryCatch({
      res.na.padj <- res[is.na(res$padj),]
      res <- res[!is.na(res$padj),] #fdrtool don't work on NA values
      res <- res[,-which(names(res) == "padj")]
      FDR.res <- fdrtool(res$stat, statistic = "normal", plot = F, verbose = F)
      res[, "padj"]  <- p.adjust(FDR.res$pval, method = "BH")
      res <- rbind(res, res.na.padj)
      padj_corrected = TRUE
    }, error = function(err) {
      return('Failed')
    }) # END tryCatch
  }
  if (padj_corrected == 'Failed') {
    res <- res_bak
  }
  res <- rbind(res, res.na.pvalue)

  res <- res %>%
    as.data.frame() %>%
    tibble::rownames_to_column(var = 'Gene') %>%
    dplyr::select(-lfcSE,-stat) %>% mutate(pass = factor('no',levels=c('yes','no'))) %>%
    mutate(pass = replace(pass, which_pass(.,thresholds),'yes') ) %>%
    mutate(Direction = factor('up',levels=c("up","down"))) %>%
    mutate(Direction = replace(Direction, which(log2FoldChange<0), 'down' ) ) %>%
    mutate(Direction = replace(Direction, which(is.na(log2FoldChange)), NA ) ) %>%
    as_data_frame()

  output <-list()
  output$res <- res
  output$padj_corrected <- padj_corrected
  
  return(output)
}


#-----------------------------------------------------------------------------

which_pass = function(res_df, thresholds){
  pass =
    res_df$baseMean >= thresholds$baseMean &
    abs(res_df$log2FoldChange) >= thresholds$log2FoldChange &
    res_df$padj <= thresholds$padj &
    !is.na(res_df$padj)

  return(which(pass))
}


#-----------------------------------------------------------------------------


create_comparison_gene_table_html = function(template_file,rdata_file,comparison,gene_db_url,replace_images=F, Rscript_exe){
  # Creates an Rmd and html of the the data for a given comaprison, based on a rmd template and the data in rdata_file
  # template_file - an Rmd file that can will be cpied and modified to fit the current comaprison
  # rdata_file - a file that contains several objects:
    # res_df - results data frame with columns: Comparison, Gene, baseMean, log2FoldChange, pvalue, padj, pass, Direction
    # dds - a DESeq object
    # comps - table of comaprisons with columns: Comparison (unique comparison name), Factor (factor for the comparison) A and B (the levels you want to compare).
  # Comparison - the comaprison name that you re interested in
  # gene_db_url - In the output there are tables with genes. They are hyperlinked with gene_db_url concatenated to the gene name.

  cmd = paste0("cat ", template_file,
              " | sed 's,__RDATA_FILE__,",rdata_file,",g' ",
              " | sed 's,__COMPARISON_NAME__,",comparison,",g' ",
              " | sed 's,$$gene_db_url,",gene_db_url,",g' ",
              " | sed 's,\\$\\$gene_db_url,\\&,g' ", #\& imcompatible between python and R cause to insertion of $$gene_db_url string
              " | sed 's,__REPLACE_IMAGES__,",replace_images,",g' ",
              " > comparison_gtab_",comparison,".Rmd"
  )
  system(cmd)

  system(paste0(Rscript_exe," -e 'library(knitr); rmarkdown::render(\"comparison_gtab_",comparison,".Rmd\")'"))

}


#-----------------------------------------------------------------------------


create_comparison_plots_html = function(template_file,rdata_file,comparison, Rscript_exe){
  # Creates an Rmd and html of the the data for a given comaprison, based on a rmd template and the data in rdata_file
  # template_file - an Rmd file that can will be cpied and modified to fit the current comaprison
    # rdata_file - a file that contains several objects:
    # res_df - results data frame with columns: Comparison, Gene, baseMean, log2FoldChange, pvalue, padj, pass, Direction
    # dds - a DESeq object
    # comps - table of comaprisons with columns: Comparison (unique comparison name), Factor (factor for the comparison) A and B (the levels you want to compare).
  # Comparison - the comaprison name that you are interested in
  # gene_db_url - In the output there are tables with genes. They are hyperlinked with gene_db_url concatenated to the gene name.

  cmd = paste0("cat ", template_file,
               " | sed 's,__RDATA_FILE__,",rdata_file,",g' ",
               " | sed 's,__COMPARISON_NAME__,",comparison,",g' ",
               " > comparison_plots_",comparison,".Rmd"
  )
  system(cmd)

  system(paste0(Rscript_exe," -e 'library(knitr); rmarkdown::render(\"comparison_plots_",comparison,".Rmd\")'"))

}

#-----------------------------------------------------------------------------


save_expression_images<- function(gene,comp_name,deseq_object,comp_df,replace_if_exists=F){

  # Create output dir
  dir.create('images', showWarnings = FALSE)

  image_name_full = paste0("images/",comp_name,"_",gene,"_","full.jpg")
  image_name_thumb = paste0("images/",comp_name,"_",gene,"_","thumb.jpg")


  # Decide wether to skip or not

  if (file.exists(image_name_full) & file.exists(image_name_thumb)){
    if (!replace_if_exists){
      warning(paste('File', image_name_full, 'and', image_name_thumb,'exist. Skipping.'))
      return(data.frame(full=image_name_full,thumb=image_name_thumb))
      # return values and stop execution
    }else{
      warning(paste('File', image_name_full, 'and', image_name_thumb,'exist. Overwriting.'))
    }
  }

  # Proceed with the main stuff

  y = "counts+1"

#  factor_name = comp_df$Factor[comp_df$Comparison==comp_name]
  factor_name = "condition"
  level1 = comp_df$A[comp_df$Comparison==comp_name]
  level2 = comp_df$B[comp_df$Comparison==comp_name]

  df4plot = cbind(sample_id = row.names(colData(deseq_object)),
                  as.data.frame(colData(deseq_object)),
                  counts = counts(deseq_object,normalize=T)[gene,]
  )
  df4plot = df4plot[df4plot[,factor_name] %in% c(level2,level1),]
  df4plot[,factor_name] = factor(df4plot[,factor_name],levels=c(level2,level1))

  gp = ggplot(data=df4plot , aes_string(x=factor_name, y=y)) +
    scale_y_continuous(trans="log2")+theme_bw(base_size = 7)+
    geom_rect(data = df4plot, aes_string(x=factor_name, y=y),
              xmin = 0,xmax = 3,ymin = 0, ymax = log2(1+10),
              alpha=0.03, fill="red"
    ) +
    geom_rect(data = df4plot, aes_string(x=factor_name, y=y),
              xmin = 0,xmax = 3,ymin = log2(1+10), ymax = log2(1+50),
              alpha=0.03, fill="yellow"
    )

  gp.full = gp +
    geom_dotplot(binaxis = "y",stackdir = "center",dotsize=0.9) +
    geom_text(aes(label=sample_id),hjust=-0.3,size=2)
  #+theme(text = element_text(size = 3))

  gp.thumb = gp +
    geom_dotplot(binaxis = "y",stackdir = "center",dotsize = 2) +
    coord_flip() +
    theme(axis.text.x = element_blank(),
          axis.text.y = element_blank(),
          axis.ticks = element_blank()) +
    labs(x="",y="")

  image_name_full = paste0("images/",comp_name,"_",gene,"_","full.jpg")
  image_name_thumb = paste0("images/",comp_name,"_",gene,"_","thumb.jpg")
  suppressMessages(ggsave(filename = image_name_full,plot = gp.full,width = 3,height = 2.5))
  suppressMessages(ggsave(filename = image_name_thumb,plot = gp.thumb,width = 1.7,height = 1))

  return(data.frame(full=image_name_full,thumb=image_name_thumb))

}


#-------------------------------------------------------------


get.most.variable <- function(norm.counts,number.to.cluster){
  logc=log2(as.matrix(norm.counts)+10)
  cv=sqrt(rowVars(logc))/rowMeans(logc)
  ord=order(cv,decreasing = T)
  return(row.names(logc)[ord[1:number.to.cluster]])
}


#-------------------------------------------------------------------------------

expression_heatmap <- function(norm.counts,genes,col.lables=colnames(norm.counts),interactive=TRUE){
  if (mode(genes)=="numeric"){
    genes = get.most.variable(norm.counts,genes)
  }

  norm.counts = norm.counts[genes,]
  A = log2(as.matrix(norm.counts)+10)
  colnames(A)=col.lables

  D.genes = Dist(A,method='pearson')
  clust.genes <- hclust(D.genes)
  dend.genes <- as.dendrogram(clust.genes)

  D.samples = Dist(t(A),method='pearson')
  clust.samples <- hclust(D.samples)
  dend.samples <- as.dendrogram(clust.samples)

  # Prepare A for the plot - subtract means and threshold points that change too much
  A.norm=(A-rowMeans(A))

  cr=colorRampPalette(c("navy", "white", "firebrick3"))(20)

  if (interactive){
    d3heatmap(A.norm,trace = 'none',dendrogram = 'both',
              Colv=dend.samples,Rowv=dend.genes,
              col = cr,cexCol = 0.8,cexRow = 0.8,show_grid = F)
  }else {
    heatmap.2(A.norm,trace = 'none',dendrogram = 'both',
              Colv=dend.samples,Rowv=dend.genes,labRow="",
              col = cr,cexCol = 0.8,cexRow = 0.8,srtCol=90)
  }

}

#-------------------------------------------------------------------------------


foldchange = function (log2fc){
  sign(log2fc)*2^abs(log2fc)
}


#-------------------------------------------------------------------------------

gene_analytics_api = function(gene_lists_vector){
  gene_analystics_html ='<!--html_preserve-->
  <div>
    <form action="https://ga.genecards.org/gene-set-analysis" method="POST" target="_blank">
      <input type="text" name="symbols" value="GENE_LIST_GOES_HERE" hidden="true">
      <input type="text" name="species" value="9606" hidden="true">
      <input type="submit" value="Send">
    </form>
  </div>
  <!--/html_preserve-->'

  out = sapply(gene_lists_vector,function(x) sub("GENE_LIST_GOES_HERE",x,gene_analystics_html))
  return(out)
}

var_elect_api = function(gene_lists_vector){
  var_elect_html ='<!--html_preserve-->
  <div>
    <form action="https://ve.genecards.org/gene-set-analysis" method="POST" target="_blank">
      <input type="text" name="symbols" value="GENE_LIST_GOES_HERE" hidden="true">
      <input type="submit" value="Send">
    </form>
  </div>
  <!--/html_preserve-->'

  out = sapply(gene_lists_vector,function(x) sub("GENE_LIST_GOES_HERE",x,var_elect_html))
  return(out)
}

#--------------------------------------------------------------------------------------

intermine_api = function(intermine_base_url, intermine_organism, gene_lists_vector) {
  html ='<!--html_preserve-->
  <div>
    <form action="INTERMINE_BASE_URL/buildBag.do" method="POST" target="_blank">
      <input type="text" name="text" value="GENE_LIST_GOES_HERE" hidden="true">
      <input type="text" name="extraFieldValue" value="INTERMINE_ORGANISM" hidden="true">
      <input type="text" name="type" value="Gene" hidden="true">
      <input type="submit" value="Send">
    </form>
  </div>
  <!--/html_preserve-->'

  html = sub("INTERMINE_BASE_URL", intermine_base_url, html);
  html = sub("INTERMINE_ORGANISM", intermine_organism, html);
  out = sapply(gene_lists_vector, function(x) sub("GENE_LIST_GOES_HERE", x, html))
  return(out)
}

#--------------------------------------------------------------------------------------

# enrichment_stats = function(bm.data ...........)

# bm.data.filt = bm.data %>%
  # filter(go_id!="") %>%
  # mutate(GO=paste(go_id,name_1006)) %>%
  # group_by(GO) %>%
  # mutate(num_in_go=n()) %>%
  # ungroup() %>%
  # filter(between(num_in_go,10,500)) %>%
  # dplyr::select(GO,Gene=ensembl_gene_id)

# You need to see handle the case of permissive vs. stringent in the function or let the user filter by base mean as the input.

# stats_per_GO_comp = res_df %>%
  # filter(baseMean>filter(thresholds,parameter=="baseMean",stringency=="permissive")$value ) %>%
  # mutate(pass.bool = pass=="stringent" | pass=="permissive") %>%
  # dplyr::select(Comparison,Gene,Direction,pass.bool) %>%
  # inner_join(bm.data.filt) %>%
  # group_by(Comparison,GO,Direction) %>%
  # summarise(num_GO_pass = sum(pass.bool),num_GO_no_pass = sum(!pass.bool))

# stats_per_comp = res_df %>%
  # filter(baseMean>filter(thresholds,parameter=="baseMean",stringency=="permissive")$value ) %>%
  # mutate(pass.bool = pass=="stringent" | pass=="permissive") %>%
  # dplyr::select(Comparison,Gene,Direction,pass.bool) %>%
  # group_by(Comparison,Direction) %>%
  # summarise(num_pass = sum(pass.bool),num_no_pass=sum(!pass.bool))

# enrich.stats = inner_join(stats_per_GO_comp,stats_per_comp) %>%
  # group_by(Comparison,GO) %>%
  # mutate(num_all=sum(num_pass)+sum(num_no_pass)) %>%
  # mutate(num_GO_all=sum(num_GO_pass)+sum(num_GO_no_pass)) %>%
  # ungroup() %>%
  # mutate(pvalue=1-phyper(q=num_GO_pass-1,m=num_GO_all,n=num_all-num_GO_all,k=num_pass)) %>%
  # mutate(FDR = p.adjust(pvalue,method ="BH")) %>%
  # dplyr::select(Comparison,Direction,GO,num_GO_pass,num_pass,num_GO_all,num_all,pvalue,FDR) %>%
  # filter(FDR<0.5) %>%
  # arrange(FDR)

