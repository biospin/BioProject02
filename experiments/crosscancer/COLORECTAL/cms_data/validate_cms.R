suppressMessages({library(CMScaller); library(Biobase)})
data(crcTCGAsubset)
pd <- pData(crcTCGAsubset)
pub <- data.frame(ID=as.character(pd$ID), CMS_pub=as.character(pd$CMS.Syn), stringsAsFactors=FALSE)
pub$bc <- substr(gsub("\\.","-",pub$ID),1,12)   # 환자 barcode 12자
mine <- read.csv("coadread_cms_cmscaller.csv", stringsAsFactors=FALSE)
mine$bc <- substr(mine$sample,1,12)
m <- merge(pub, mine, by="bc")
m <- m[!is.na(m$CMS_pub) & m$CMS_pub!="" ,]
cat("공개콜 대조 가능 샘플:", nrow(m), "\n\n")
cat("confusion (행=published CMS.Syn, 열=내 CMScaller):\n")
print(table(published=m$CMS_pub, mine=m$CMS))
agree <- mean(m$CMS_pub==m$CMS, na.rm=TRUE)
cat(sprintf("\n일치율(concordance): %.1f%% (%d/%d)\n", agree*100, sum(m$CMS_pub==m$CMS,na.rm=TRUE), nrow(m)))
