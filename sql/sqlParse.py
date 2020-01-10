__author__ = 'menghui'
import sqlparse

unavailableKeyWord = [u"DELETE", u"UPDATE", u"INSERT", u"CREATE", u"DROP", u"ALTER", u"INTO", u"REPLACE", u"MERGE"]


def availableKeyWord(p):
    if hasattr(p, "ttype") and hasattr(p, "normalized"):
        if p.ttype == sqlparse.tokens.Token.Keyword or p.ttype == sqlparse.tokens.Token.Keyword.DML:
            if p.normalized in unavailableKeyWord:
                return False
    if hasattr(p, "tokens"):
        for t in p.tokens:
            r = availableKeyWord(t)
            if not r:
                return False
    return True


def availableSQL(sql):
    p = sqlparse.parse(sql)
    if len(p) != 1:
        return False
    if p[0].tokens[0].ttype == sqlparse.tokens.Token.Keyword.DML and p[0].tokens[0].normalized == "SELECT":
        return True
    if p[0].tokens[0].ttype == sqlparse.tokens.Token.Keyword and p[0].tokens[0].normalized == "WITH":
        return True
    return False


def addPrefix(tokens):
    for item in tokens:
        if hasattr(item, 'tokens'):
            addPrefix(item.tokens)
        if isinstance(item, sqlparse.sql.Identifier):
            item.value = 'src.' + item.value
            print(item.value)


if __name__ == "__main__":
    sql = "SELECT src.*, stu.st_stbprp_b.stnm  from (SELECT stcd,tm,z,q,wptn FROM stu.ST_RIVER_R WHERE stcd='81211';drop table ass;//) src inner join  stu.st_stbprp_b on st_stbprp_b.stcd=src.stcd"

    sql = '''with result_table as
     (select s1.startdate stdt,
             s1.col_1 addvcd,
             to_number(s2.col_2) CRDIASUM,
             to_number(s2.col_4) CRDNASUM,
             to_number(s1.COL_4) DIPOP,
             to_number(s1.COL_7) DEPOP,
             to_number(s1.COL_8) MIPOP,
             to_number(s1.COL_6) COHOU,
             to_number(s1.COL_10) ECLOSS,
             to_number(s3.COL_19) DISWATERFACRATIO
        from shzh_business_report_01_m s1,
             shzh_business_report_02_m s2,
             shzh_business_report_04_m s3
       where s1.col_1 = s2.col_1
         and s1.col_1 = s3.col_1
         and s1.startdate = s2.startdate
         and s1.startdate = s3.startdate),
    sum_result as
     (select '合计' as addvnm,
             '0' as addvcd,
             sum(CRDIASUM) CRDIASUM,
             sum(CRDNASUM) CRDNASUM,
             sum(DIPOP) DIPOP,
             sum(DEPOP) DEPOP,
             sum(MIPOP) MIPOP,
             sum(COHOU) COHOU,
             sum(ECLOSS) ECLOSS,
             sum(DISWATERFACRATIO) DISWATERFACRATIO
        from result_table a
       where a.stdt like '2015-03%'),
    first_result_table as
     (select a.addvnm,
             b.addvcd,
             CRDIASUM,
             CRDNASUM,
             DIPOP,
             DEPOP,
             MIPOP,
             COHOU,
             ECLOSS,
             DISWATERFACRATIO
        from (select '2014年同期值' addvnm, '1' addvcd, '2014-03' as year
                from dual) a
        left join (select '2014年同期值' addvnm,
                         '1' addvcd,
                         sum(CRDIASUM) CRDIASUM,
                         sum(CRDNASUM) CRDNASUM,
                         sum(DIPOP) DIPOP,
                         sum(DEPOP) DEPOP,
                         sum(MIPOP) MIPOP,
                         sum(COHOU) COHOU,
                         sum(ECLOSS) ECLOSS,
                         sum(DISWATERFACRATIO) DISWATERFACRATIO,
                         stdt
                    from result_table r
                   group by r.stdt) b
          on a.addvcd = b.addvcd
         and b.stdt like a.year || '%'),
    result_20_table as
     (select a.addvnm,
             a.addvcd,
             CRDIASUM,
             CRDNASUM,
             DIPOP,
             DEPOP,
             MIPOP,
             COHOU,
             ECLOSS,
             DISWATERFACRATIO
        from (select '1990年同期值' addvnm, '1' addvcd from dual) a
        left join (select *
                    from (select '1990年同期值' addvnm,
                                 '1' addvcd,
                                 sum(CRDIASUM) CRDIASUM,
                                 sum(CRDNASUM) CRDNASUM,
                                 sum(DIPOP) DIPOP,
                                 sum(DEPOP) DEPOP,
                                 sum(MIPOP) MIPOP,
                                 sum(COHOU) COHOU,
                                 sum(ECLOSS) ECLOSS,
                                 sum(DISWATERFACRATIO) DISWATERFACRATIO,
                                 stdt
                            from result_table r
                           group by r.stdt)
                   where stdt like '1990-03%') b
          on a.addvcd = b.addvcd),
    result_10_table as
     (select a.addvnm,
             a.addvcd,
             CRDIASUM,
             CRDNASUM,
             DIPOP,
             DEPOP,
             MIPOP,
             COHOU,
             ECLOSS,
             DISWATERFACRATIO
        from (select '2000年同期值' addvnm, '1' addvcd from dual) a
        left join (select *
                    from (select '2000年同期值' addvnm,
                                 '1' addvcd,
                                 sum(CRDIASUM) CRDIASUM,
                                 sum(CRDNASUM) CRDNASUM,
                                 sum(DIPOP) DIPOP,
                                 sum(DEPOP) DEPOP,
                                 sum(MIPOP) MIPOP,
                                 sum(COHOU) COHOU,
                                 sum(ECLOSS) ECLOSS,
                                 sum(DISWATERFACRATIO) DISWATERFACRATIO,
                                 stdt
                            from result_table r
                           group by r.stdt)
                   where stdt like '2000-03%') b
          on a.addvcd = b.addvcd)
    select *
      from sum_result
    union all
    select *
      from result_20_table
    union all
    select '距平' addvnm,
           '1' addvcd,
           round((s.CRDIASUM - f.CRDIASUM) / f.CRDIASUM * 100, 2) CRDIASUM,
           round((s.CRDNASUM - f.CRDNASUM) / f.CRDNASUM * 100, 2) CRDNASUM,
           round((s.DIPOP - f.DIPOP) / f.DIPOP * 100, 2) DIPOP,
           round((s.DEPOP - f.DEPOP) / f.DEPOP * 100, 2) DEPOP,
           round((s.MIPOP - f.MIPOP) / f.MIPOP * 100, 2) MIPOP,
           round((s.COHOU - f.COHOU) / f.COHOU * 100, 2) COHOU,
           round((s.ECLOSS - f.ECLOSS) / f.ECLOSS * 100, 2) ECLOSS,
           round((s.DISWATERFACRATIO - f.DISWATERFACRATIO) / f.DISWATERFACRATIO * 100,
                 2) DISWATERFACRATIO
      from sum_result s, result_20_table f
    union all
    select *
      from result_10_table
    union all
    select '距平' addvnm,
           '1' addvcd,
           round((s.CRDIASUM - f.CRDIASUM) / f.CRDIASUM * 100, 2) CRDIASUM,
           round((s.CRDNASUM - f.CRDNASUM) / f.CRDNASUM * 100, 2) CRDNASUM,
           round((s.DIPOP - f.DIPOP) / f.DIPOP * 100, 2) DIPOP,
           round((s.DEPOP - f.DEPOP) / f.DEPOP * 100, 2) DEPOP,
           round((s.MIPOP - f.MIPOP) / f.MIPOP * 100, 2) MIPOP,
           round((s.COHOU - f.COHOU) / f.COHOU * 100, 2) COHOU,
           round((s.ECLOSS - f.ECLOSS) / f.ECLOSS * 100, 2) ECLOSS,
           round((s.DISWATERFACRATIO - f.DISWATERFACRATIO) / f.DISWATERFACRATIO * 100,
                 2) DISWATERFACRATIO
      from sum_result s, result_10_table f
    union all
    select *
      from first_result_table
    union all
    select '距平' addvnm,
           '1' addvcd,
           round((s.CRDIASUM - f.CRDIASUM) / f.CRDIASUM * 100, 2) CRDIASUM,
           round((s.CRDNASUM - f.CRDNASUM) / f.CRDNASUM * 100, 2) CRDNASUM,
           round((s.DIPOP - f.DIPOP) / f.DIPOP * 100, 2) DIPOP,
           round((s.DEPOP - f.DEPOP) / f.DEPOP * 100, 2) DEPOP,
           round((s.MIPOP - f.MIPOP) / f.MIPOP * 100, 2) MIPOP,
           round((s.COHOU - f.COHOU) / f.COHOU * 100, 2) COHOU,
           round((s.ECLOSS - f.ECLOSS) / f.ECLOSS * 100, 2) ECLOSS,
           round((s.DISWATERFACRATIO - f.DISWATERFACRATIO) / f.DISWATERFACRATIO * 100,
                 2) DISWATERFACRATIO
      from sum_result s, first_result_table f
    union all
    select *
      from (select a.addvnm,
                   a.addvcd,
                   CRDIASUM,
                   CRDNASUM,
                   DIPOP,
                   DEPOP,
                   MIPOP,
                   COHOU,
                   ECLOSS,
                   DISWATERFACRATIO
              from (select s.addvcd, s.addvnm
                      from user_5402.SE_ADDV_C s
                     WHERE s.addvcd like '__0000') a
              left join (select *
                          from result_table b
                         where b.stdt like '2015-03%') tb
                on a.addvcd = tb.addvcd
             order by addvcd)
    '''
    p = sqlparse.parse(sql)
    s = ""
    #addPrefix(p[0].tokens)
    print(availableSQL(sql))
