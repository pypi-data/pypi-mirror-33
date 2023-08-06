<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:sch="http://purl.oclc.org/dsdl/schematron">

    <xsl:output method="xml" encoding="utf-8" indent="yes"/>

    <xsl:template match="/">
    	<sch:schema>
    		<xsl:apply-templates select="//sch:ns"/>
    		<xsl:apply-templates select="//sch:phase"/>
    		<xsl:apply-templates select="//sch:pattern"/>
			<xsl:if test="//sch:rule[not(ancestor::sch:pattern)]">
				<sch:pattern name="">
					<xsl:apply-templates select="//sch:rule[not(ancestor::sch:pattern)]"/>
				</sch:pattern>
			</xsl:if>
			<xsl:if test="//sch:diagnostics">
				<sch:diagnostics>
					<xsl:apply-templates select="//sch:diagnostics/*"/>
				</sch:diagnostics>				
			</xsl:if>
    	</sch:schema>
    </xsl:template>

    <xsl:template match="sch:*" name="sch-element">
    	<xsl:param name="element" select="."/>
    	<xsl:element name="{$element/name()}">
    		<xsl:apply-templates select="@*|*|node()"/>
    	</xsl:element>
    </xsl:template>

    <xsl:template match="@*">
    	<xsl:attribute name="{name()}">
			<xsl:value-of select="."/>
		</xsl:attribute>
    </xsl:template>

    <xsl:template match="text()">
    	<xsl:copy-of select="."/>
    </xsl:template>

</xsl:stylesheet>